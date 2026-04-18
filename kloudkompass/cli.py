# kloudkompass/cli.py
# -----------------
# the main CLI entrypoint using Click. This is what runs
# when you type 'kloudkompass' in the terminal. Uses the factory pattern to
# get providers, so the CLI does not need to know about AWS/Azure/GCP details.

import sys
import click
from typing import Optional

from kloudkompass import __version__, __copyright__
from kloudkompass.core import get_cost_provider, KloudKompassError, get_available_providers
from kloudkompass.config_manager import merge_cli_with_config, get_config_path, set_config_value
from kloudkompass.utils.logger import set_debug_mode, get_logger
from kloudkompass.utils.formatters import format_records, OutputFormat
from kloudkompass.utils.exports import export_records, generate_default_filename


# Sets up help text that explains what the tool does
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option(
    version=__version__,
    prog_name="kloudkompass",
    message=f"%(prog)s %(version)s\n{__copyright__}\nKloud Kompass is open-source software."
)
@click.option(
    '--debug/--no-debug',
    default=False,
    help="Enable debug output for troubleshooting."
)
@click.pass_context
def main(ctx, debug):
    """
    Kloud Kompass - Terminal-first multi-cloud CLI.
    
    A command-line tool for cloud practitioners who prefer terminal workflows.
    Query costs, inventory, and security across AWS, Azure, and GCP.
    
    Run without a subcommand to launch the interactive TUI.
    
    Examples:
    
      kloudkompass                      # Launch interactive TUI
      
      kloudkompass dashboard            # Launch Textual dashboard
      
      kloudkompass cost --provider aws --start 2024-01-01 --end 2024-02-01
      
      kloudkompass config --set-default-provider aws
    """
    # Store debug flag in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    
    if debug:
        set_debug_mode(True)
        get_logger().debug("Debug mode enabled")
    
    # If no subcommand, launch TUI
    if ctx.invoked_subcommand is None:
        from kloudkompass.tui import launch
        launch()


@main.command()
@click.option(
    '--provider', '-p',
    type=click.Choice(['aws', 'azure', 'gcp'], case_sensitive=False),
    help="Cloud provider to query. Default: aws"
)
@click.option(
    '--start', '-s',
    required=True,
    help="Start date in YYYY-MM-DD format."
)
@click.option(
    '--end', '-e',
    required=True,
    help="End date in YYYY-MM-DD format."
)
@click.option(
    '--breakdown', '-b',
    type=click.Choice(['total', 'service', 'usage', 'daily'], case_sensitive=False),
    default='service',
    help="How to break down costs. Default: service"
)
@click.option(
    '--threshold', '-t',
    type=float,
    default=0.0,
    help="Hide costs below this threshold. Default: 0"
)
@click.option(
    '--profile',
    help="Cloud provider profile/account to use."
)
@click.option(
    '--region',
    help="Cloud provider region (not used for cost queries on most providers)."
)
@click.option(
    '--output', '-o',
    type=click.Choice(['table', 'plain', 'json', 'csv'], case_sensitive=False),
    default='table',
    help="Output format. Default: table"
)
@click.option(
    '--export',
    type=click.Path(),
    help="Export results to file (CSV or JSON based on extension)."
)
@click.pass_context
def cost(ctx, provider, start, end, breakdown, threshold, profile, region, output, export):
    """
    Fetch cloud costs for a date range.
    
    Query billing data from AWS, Azure, or GCP. Results can be broken down
    by service, usage type, or daily. Use --threshold to filter small costs.
    
    Examples:
    
      kloudkompass cost --provider aws --start 2024-01-01 --end 2024-02-01
      
      kloudkompass cost -p aws -s 2024-01-01 -e 2024-02-01 --breakdown daily
      
      kloudkompass cost -p aws -s 2024-12-01 -e 2025-01-01 --threshold 5 --output json
    """
    try:
        # Merge CLI args with saved config
        config = merge_cli_with_config(
            provider=provider,
            profile=profile,
            region=region,
            output=output,
            debug=ctx.obj.get('debug'),
        )
        
        effective_provider = config['provider']
        effective_output = config['output']
        
        # Get the appropriate cost provider
        cost_provider = get_cost_provider(effective_provider)
        
        # Show what we are doing
        click.echo(f"Fetching {breakdown} costs for {effective_provider.upper()}...")
        click.echo(f"Date range: {start} to {end}")
        if threshold > 0:
            click.echo(f"Threshold: ${threshold:.2f}")
        click.echo()
        
        # Fetch cost data
        records = cost_provider.get_cost(
            start_date=start,
            end_date=end,
            breakdown=breakdown,
            profile=config['profile'],
            region=config['region'],
        )
        
        # Apply threshold filter
        if threshold > 0:
            records = cost_provider.filter_by_threshold(records, threshold)
        
        if not records:
            click.echo("No cost data found for the specified criteria.")
            return
        
        # Display results
        title = f"{effective_provider.upper()} Costs - {breakdown.capitalize()} Breakdown"
        output_format = OutputFormat(effective_output)
        format_records(records, output_format, title=title)
        
        # Export if requested
        if export:
            # Determine format from extension
            if export.endswith('.json'):
                export_format = 'json'
            else:
                export_format = 'csv'
            
            exported_path = export_records(records, export, format=export_format)
            click.echo(f"\nExported to: {exported_path}")
            
    except KloudKompassError as e:
        # Catches our custom errors and display them nicely
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled.", err=True)
        sys.exit(130)
    except Exception as e:
        # Unexpected errors get full traceback in debug mode
        if ctx.obj.get('debug'):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        click.echo("Run with --debug for more details.", err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--provider', '-p',
    type=click.Choice(['aws', 'azure', 'gcp'], case_sensitive=False),
    help="Cloud provider to query. Default: aws"
)
@click.option(
    '--state', '-s',
    type=click.Choice(['running', 'stopped', 'terminated', 'all'], case_sensitive=False),
    default='all',
    help="Filter instances by state."
)
@click.option(
    '--profile',
    help="Cloud provider profile/account to use."
)
@click.option(
    '--region',
    help="Cloud provider region."
)
@click.option(
    '--output', '-o',
    type=click.Choice(['table', 'plain', 'json', 'csv'], case_sensitive=False),
    default='table',
    help="Output format. Default: table"
)
@click.option(
    '--export',
    type=click.Path(),
    help="Export results to file (CSV or JSON based on extension)."
)
@click.option(
    '--tag',
    multiple=True,
    help="Filter by tag (Key=Value). Can be specified multiple times."
)
@click.option(
    '--type',
    'instance_type',
    help="Filter by instance type (e.g. t2.micro, m5.large)."
)
@click.option(
    '--az',
    help="Filter by Availability Zone (e.g. us-east-1a)."
)
@click.option('--target', multiple=True, help="Instance IDs to target for batch operations.")
@click.option('--start', is_flag=True, help="Start specified instances.")
@click.option('--stop', is_flag=True, help="Stop specified instances.")
@click.option('--add-tag', multiple=True, help="Add/update tag (Key=Value).")
@click.option('--remove-tag', multiple=True, help="Remove tag by Key.")
@click.pass_context
def compute(ctx, provider, state, profile, region, output, export, tag, instance_type, az, target, start, stop, add_tag, remove_tag):
    """
    List or manage compute instances (e.g. EC2/VMs).
    
    Examples:
      kloudkompass compute
      kloudkompass compute --state running
      kloudkompass compute --start --target i-xxxx --target i-yyyy
      kloudkompass compute --add-tag Env=Prod --target i-xxxx
    """
    from kloudkompass.core.provider_factory import get_compute_provider
    try:
        config = merge_cli_with_config(
            provider=provider,
            profile=profile,
            region=region,
            output=output,
            debug=ctx.obj.get('debug'),
        )
        
        effective_provider = config['provider']
        compute_provider = get_compute_provider(effective_provider)

        # Batch Operations Logic
        has_action = start or stop or add_tag or remove_tag
        if has_action:
            if not target:
                click.echo("Error: --target is required when specifying an action (--start, --stop, --add-tag, --remove-tag).", err=True)
                sys.exit(1)
                
            targets_list = list(target)
            
            if start:
                click.echo(f"Starting {len(targets_list)} instance(s)...")
                if compute_provider.start_instance(targets_list, region=config['region'], profile=config['profile']):
                    click.echo("✓ Start command accepted.")
                else:
                    click.echo("✗ Start command failed.", err=True)
                    
            if stop:
                click.echo(f"Stopping {len(targets_list)} instance(s)...")
                if compute_provider.stop_instance(targets_list, region=config['region'], profile=config['profile']):
                    click.echo("✓ Stop command accepted.")
                else:
                    click.echo("✗ Stop command failed.", err=True)
                    
            if add_tag:
                tags_to_add = {}
                for t in add_tag:
                    if '=' not in t:
                        click.echo(f"Error: Invalid tag format '{t}'. Must be Key=Value.", err=True)
                        sys.exit(1)
                    k, v = t.split('=', 1)
                    tags_to_add[k] = v
                    
                click.echo(f"Adding {len(tags_to_add)} tag(s) to {len(targets_list)} instance(s)...")
                if compute_provider.add_tags(targets_list, tags_to_add, region=config['region'], profile=config['profile']):
                    click.echo("✓ Tags added.")
                else:
                    click.echo("✗ Failed to add tags.", err=True)
                    
            if remove_tag:
                keys_to_remove = list(remove_tag)
                click.echo(f"Removing {len(keys_to_remove)} tag(s) from {len(targets_list)} instance(s)...")
                if compute_provider.remove_tags(targets_list, keys_to_remove, region=config['region'], profile=config['profile']):
                    click.echo("✓ Tags removed.")
                else:
                    click.echo("✗ Failed to remove tags.", err=True)
                    
            return # Exit early, skip normal listing
            
        click.echo(f"Fetching compute instances for {effective_provider.upper()}...")
        if state != 'all':
            click.echo(f"Filter: state={state}")
        if target:
            click.echo(f"Target filter: {target}")
        click.echo()
        
        filters = {}
        if state != 'all':
            if effective_provider == 'aws':
                filters['instance-state-name'] = state
        if instance_type and effective_provider == 'aws':
            filters['instance-type'] = instance_type
        if az and effective_provider == 'aws':
            filters['availability-zone'] = az
            
        if not filters:
            filters = None
                
        tags_dict = None
        if tag:
            tags_dict = {}
            for t in tag:
                if '=' in t:
                    k, v = t.split('=', 1)
                    tags_dict[k] = v
                else:
                    tags_dict[t] = ""
            
        instances = compute_provider.list_instances(
            region=config['region'],
            profile=config['profile'],
            filters=filters,
            tags=tags_dict,
        )
        
        if not instances:
            click.echo("No instances found.")
            return
            
        # Display results using our formatter
        title = f"{effective_provider.upper()} Compute Instances"
        output_format = OutputFormat(config['output'])
        format_records(instances, output_format, title=title)
        
        if export:
            export_format = 'json' if export.endswith('.json') else 'csv'
            exported_path = export_records(instances, export, format=export_format)
            click.echo(f"\nExported to: {exported_path}")
            
    except KloudKompassError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled.", err=True)
        sys.exit(130)
    except Exception as e:
        if ctx.obj.get('debug'):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--provider', '-p', type=click.Choice(['aws', 'azure', 'gcp'], case_sensitive=False), help="Cloud provider to query.")
@click.option('--type', '-t', 'resource_type', type=click.Choice(['vpc', 'subnet', 'sg'], case_sensitive=False), default='vpc', help="Resource type to list.")
@click.option('--profile', help="Cloud provider profile/account to use.")
@click.option('--region', help="Cloud provider region.")
@click.option('--output', '-o', type=click.Choice(['table', 'plain', 'json', 'csv'], case_sensitive=False), default='table', help="Output format.")
@click.option('--export', type=click.Path(), help="Export results to file.")
@click.option('--tag', multiple=True, help="Filter by tag (Key=Value). Can be specified multiple times.")
@click.pass_context
def network(ctx, provider, resource_type, profile, region, output, export, tag):
    """List network resources (VPCs, Subnets, Security Groups)."""
    from kloudkompass.core.provider_factory import get_network_provider
    try:
        config = merge_cli_with_config(provider=provider, profile=profile, region=region, output=output, debug=ctx.obj.get('debug'))
        effective_provider = config['provider']
        network_provider = get_network_provider(effective_provider)
        
        tags_dict = None
        if tag:
            tags_dict = {}
            for t in tag:
                if '=' in t:
                    k, v = t.split('=', 1)
                    tags_dict[k] = v
                else:
                    tags_dict[t] = ""
                    
        click.echo(f"Fetching {resource_type.upper()}s for {effective_provider.upper()}...")
        if resource_type == 'vpc':
            records = network_provider.list_vpcs(region=config['region'], profile=config['profile'], tags=tags_dict)
        elif resource_type == 'subnet':
            records = network_provider.list_subnets(region=config['region'], profile=config['profile'], tags=tags_dict)
        else:
            records = network_provider.list_security_groups(region=config['region'], profile=config['profile'], tags=tags_dict)
            
        if not records:
            click.echo(f"No {resource_type.upper()}s found.")
            return
            
        format_records(records, OutputFormat(config['output']), title=f"{effective_provider.upper()} {resource_type.upper()}s")
        if export:
            export_format = 'json' if export.endswith('.json') else 'csv'
            click.echo(f"\nExported to: {export_records(records, export, format=export_format)}")
    except KloudKompassError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--provider', '-p', type=click.Choice(['aws', 'azure', 'gcp'], case_sensitive=False), help="Cloud provider to query.")
@click.option('--type', '-t', 'resource_type', type=click.Choice(['bucket', 'volume'], case_sensitive=False), default='bucket', help="Resource type to list.")
@click.option('--profile', help="Cloud provider profile/account to use.")
@click.option('--region', help="Cloud provider region.")
@click.option('--output', '-o', type=click.Choice(['table', 'plain', 'json', 'csv'], case_sensitive=False), default='table', help="Output format.")
@click.option('--export', type=click.Path(), help="Export results to file.")
@click.option('--tag', multiple=True, help="Filter by tag (Key=Value). Can be specified multiple times.")
@click.option('--bucket-region', help="Filter S3 buckets by region.")
@click.option('--public-access', type=click.Choice(['public', 'private'], case_sensitive=False), help="Filter S3 buckets by public access.")
@click.pass_context
def storage(ctx, provider, resource_type, profile, region, output, export, tag, bucket_region, public_access):
    """List storage resources (S3 Buckets, EBS Volumes)."""
    from kloudkompass.core.provider_factory import get_storage_provider
    try:
        config = merge_cli_with_config(provider=provider, profile=profile, region=region, output=output, debug=ctx.obj.get('debug'))
        effective_provider = config['provider']
        storage_provider = get_storage_provider(effective_provider)
        
        tags_dict = None
        if tag:
            tags_dict = {}
            for t in tag:
                if '=' in t:
                    k, v = t.split('=', 1)
                    tags_dict[k] = v
                else:
                    tags_dict[t] = ""
                    
        filters = {}
        if bucket_region and effective_provider == 'aws':
            filters['region'] = bucket_region
        if public_access and effective_provider == 'aws':
            filters['public-access'] = public_access
            
        if not filters:
            filters = None
            
        click.echo(f"Fetching {resource_type.capitalize()}s for {effective_provider.upper()}...")
        if resource_type == 'bucket':
            records = storage_provider.list_buckets(profile=config['profile'], tags=tags_dict, filters=filters)
        else:
            records = storage_provider.list_volumes(region=config['region'], profile=config['profile'], tags=tags_dict)
            
        if not records:
            click.echo(f"No {resource_type}s found.")
            return
            
        format_records(records, OutputFormat(config['output']), title=f"{effective_provider.upper()} Storage ({resource_type.capitalize()}s)")
        if export:
            export_format = 'json' if export.endswith('.json') else 'csv'
            click.echo(f"\nExported to: {export_records(records, export, format=export_format)}")
    except KloudKompassError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--provider', '-p', type=click.Choice(['aws', 'azure', 'gcp'], case_sensitive=False), help="Cloud provider to query.")
@click.option('--type', '-t', 'resource_type', type=click.Choice(['user', 'role', 'policy'], case_sensitive=False), default='user', help="Resource type to list.")
@click.option('--profile', help="Cloud provider profile/account to use.")
@click.option('--output', '-o', type=click.Choice(['table', 'plain', 'json', 'csv'], case_sensitive=False), default='table', help="Output format.")
@click.option('--export', type=click.Path(), help="Export results to file.")
@click.pass_context
def iam(ctx, provider, resource_type, profile, output, export):
    """List IAM resources (Users, Roles, Policies)."""
    from kloudkompass.core.provider_factory import get_iam_provider
    try:
        config = merge_cli_with_config(provider=provider, profile=profile, output=output, debug=ctx.obj.get('debug'))
        effective_provider = config['provider']
        iam_provider = get_iam_provider(effective_provider)
        
        click.echo(f"Fetching {resource_type.capitalize()}s for {effective_provider.upper()}...")
        if resource_type == 'user':
            records = iam_provider.list_users(profile=config['profile'])
        elif resource_type == 'role':
            records = iam_provider.list_roles(profile=config['profile'])
        else:
            records = iam_provider.list_policies(profile=config['profile'])
            
        if not records:
            click.echo(f"No {resource_type}s found.")
            return
            
        format_records(records, OutputFormat(config['output']), title=f"{effective_provider.upper()} IAM ({resource_type.capitalize()}s)")
        if export:
            export_format = 'json' if export.endswith('.json') else 'csv'
            click.echo(f"\nExported to: {export_records(records, export, format=export_format)}")
    except KloudKompassError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--provider', '-p', type=click.Choice(['aws', 'azure', 'gcp'], case_sensitive=False), help="Cloud provider to query.")
@click.option('--type', '-t', 'resource_type', type=click.Choice(['rds', 'nosql', 'dynamodb'], case_sensitive=False), default='rds', help="Resource type to list.")
@click.option('--profile', help="Cloud provider profile/account to use.")
@click.option('--region', help="Cloud provider region.")
@click.option('--output', '-o', type=click.Choice(['table', 'plain', 'json', 'csv'], case_sensitive=False), default='table', help="Output format.")
@click.option('--export', type=click.Path(), help="Export results to file.")
@click.pass_context
def database(ctx, provider, resource_type, profile, region, output, export):
    """List databases (RDS, DynamoDB)."""
    from kloudkompass.core.provider_factory import get_database_provider
    try:
        config = merge_cli_with_config(provider=provider, profile=profile, region=region, output=output, debug=ctx.obj.get('debug'))
        effective_provider = config['provider']
        db_provider = get_database_provider(effective_provider)
        
        click.echo(f"Fetching {resource_type.upper()} instances for {effective_provider.upper()}...")
        if resource_type == 'rds':
            records = db_provider.list_db_instances(region=config['region'], profile=config['profile'])
        else:
            records = db_provider.list_nosql_tables(region=config['region'], profile=config['profile'])
            
        if not records:
            click.echo(f"No {resource_type.upper()} databases found.")
            return
            
        format_records(records, OutputFormat(config['output']), title=f"{effective_provider.upper()} Databases ({resource_type.upper()})")
        if export:
            export_format = 'json' if export.endswith('.json') else 'csv'
            click.echo(f"\nExported to: {export_records(records, export, format=export_format)}")
    except KloudKompassError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--show',
    is_flag=True,
    help="Show current configuration."
)
@click.option(
    '--set-default-provider',
    type=click.Choice(['aws', 'azure', 'gcp'], case_sensitive=False),
    help="Set default cloud provider."
)
@click.option(
    '--set-default-output',
    type=click.Choice(['table', 'plain', 'json', 'csv'], case_sensitive=False),
    help="Set default output format."
)
@click.option(
    '--set-default-profile',
    help="Set default profile name."
)
@click.option(
    '--set-default-region',
    help="Set default region."
)
def config(show, set_default_provider, set_default_output, set_default_profile, set_default_region):
    """
    View or modify Kloud Kompass configuration.
    
    Configuration is stored in ~/.kloudkompass/config.toml
    
    Examples:
    
      kloudkompass config --show
      
      kloudkompass config --set-default-provider aws
      
      kloudkompass config --set-default-output table
    """
    try:
        if show:
            from kloudkompass.config_manager import load_config
            config = load_config()
            click.echo(f"Configuration file: {get_config_path()}")
            click.echo()
            for key, value in config.items():
                display_value = value if value is not None else "(not set)"
                click.echo(f"  {key}: {display_value}")
            return
        
        # Handle setting values
        if set_default_provider:
            set_config_value("default_provider", set_default_provider.lower())
            click.echo(f"Default provider set to: {set_default_provider.lower()}")
        
        if set_default_output:
            set_config_value("default_output", set_default_output.lower())
            click.echo(f"Default output set to: {set_default_output.lower()}")
        
        if set_default_profile:
            set_config_value("default_profile", set_default_profile)
            click.echo(f"Default profile set to: {set_default_profile}")
        
        if set_default_region:
            set_config_value("default_region", set_default_region)
            click.echo(f"Default region set to: {set_default_region}")
        
        # If no options given, show help
        if not any([show, set_default_provider, set_default_output, 
                    set_default_profile, set_default_region]):
            click.echo("Use --show to view configuration or --set-* options to modify.")
            click.echo("Run 'kloudkompass config --help' for all options.")
            
    except KloudKompassError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--provider', '-p',
    type=click.Choice(['aws', 'azure', 'gcp', 'all'], case_sensitive=False),
    default='all',
    help="Check specific provider or all. Default: all"
)
def check(provider):
    """
    Check CLI availability and credentials.
    
    Verifies that provider CLIs are installed and credentials are configured.
    
    Examples:
    
      kloudkompass check
      
      kloudkompass check --provider aws
    """
    from kloudkompass.core.health import check_cli_installed, check_credentials
    
    providers = ['aws', 'azure', 'gcp'] if provider == 'all' else [provider]
    
    cli_names = {
        'aws': 'aws',
        'azure': 'az',
        'gcp': 'gcloud',
    }
    
    any_issues = False
    
    for p in providers:
        cli_name = cli_names[p]
        click.echo(f"\n{p.upper()}:")
        
        # Check CLI installed
        if check_cli_installed(cli_name):
            click.echo(f"  CLI ({cli_name}): Installed")
        else:
            click.echo(f"  CLI ({cli_name}): Not found")
            any_issues = True
            continue
        
        # Check credentials
        is_valid, error = check_credentials(p)
        if is_valid:
            click.echo(f"  Credentials: Valid")
        else:
            click.echo(f"  Credentials: {error}")
            any_issues = True
    
    click.echo()
    if any_issues:
        click.echo("Some checks failed. See above for details.")
        sys.exit(1)
    else:
        click.echo("All checks passed.")


@main.command()
def doctor():
    """
    Run environment health checks.
    
    Checks CLI installations, credentials, and configuration.
    This is a detailed diagnostic tool for troubleshooting.
    
    Examples:
    
      kloudkompass doctor
    """
    from kloudkompass.tui.doctor import print_doctor_report
    all_passed = print_doctor_report()
    if not all_passed:
        sys.exit(1)


@main.command()
def dashboard():
    """
    Launch the Textual-based dashboard.
    
    A full-featured terminal dashboard with:
    - Sidebar navigation
    - Keyboard shortcuts
    - Live data refresh
    - Scrollable tables
    
    Examples:
    
      kloudkompass dashboard
    """
    try:
        from kloudkompass.dashboard import launch_dashboard
        launch_dashboard()
    except ImportError:
        click.echo("Error: Dashboard requires 'textual' package.", err=True)
        click.echo("Install with: pip install textual", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
