# bashcloud/cli.py
# -----------------
# the main CLI entrypoint using Click. This is what runs
# when you type 'bashcloud' in the terminal. Uses the factory pattern to
# get providers, so the CLI does not need to know about AWS/Azure/GCP details.

import sys
import click
from typing import Optional

from bashcloud import __version__
from bashcloud.core import get_cost_provider, BashCloudError, get_available_providers
from bashcloud.config_manager import merge_cli_with_config, get_config_path, set_config_value
from bashcloud.utils.logger import set_debug_mode, get_logger
from bashcloud.utils.formatters import format_records, OutputFormat
from bashcloud.utils.exports import export_records, generate_default_filename


# Sets up help text that explains what the tool does
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="bashcloud")
@click.option(
    '--debug/--no-debug',
    default=False,
    help="Enable debug output for troubleshooting."
)
@click.pass_context
def main(ctx, debug):
    """
    BashCloud - Terminal-first multi-cloud CLI.
    
    A command-line tool for cloud practitioners who prefer terminal workflows.
    Query costs, inventory, and security across AWS, Azure, and GCP.
    
    Run without a subcommand to launch the interactive TUI.
    
    Examples:
    
      bashcloud                      # Launch interactive TUI
      
      bashcloud dashboard            # Launch Textual dashboard
      
      bashcloud cost --provider aws --start 2024-01-01 --end 2024-02-01
      
      bashcloud config --set-default-provider aws
    """
    # Store debug flag in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    
    if debug:
        set_debug_mode(True)
        get_logger().debug("Debug mode enabled")
    
    # If no subcommand, launch TUI
    if ctx.invoked_subcommand is None:
        from bashcloud.tui import launch
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
    
      bashcloud cost --provider aws --start 2024-01-01 --end 2024-02-01
      
      bashcloud cost -p aws -s 2024-01-01 -e 2024-02-01 --breakdown daily
      
      bashcloud cost -p aws -s 2024-12-01 -e 2025-01-01 --threshold 5 --output json
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
            
    except BashCloudError as e:
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
    '--show',
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
    View or modify BashCloud configuration.
    
    Configuration is stored in ~/.bashcloud/config.toml
    
    Examples:
    
      bashcloud config --show
      
      bashcloud config --set-default-provider aws
      
      bashcloud config --set-default-output table
    """
    try:
        if show:
            from bashcloud.config_manager import load_config
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
            click.echo("Run 'bashcloud config --help' for all options.")
            
    except BashCloudError as e:
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
    
      bashcloud check
      
      bashcloud check --provider aws
    """
    from bashcloud.core.health import check_cli_installed, check_credentials
    
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
    
      bashcloud doctor
    """
    from bashcloud.tui.doctor import print_doctor_report
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
    
      bashcloud dashboard
    """
    try:
        from bashcloud.dashboard import launch_dashboard
        launch_dashboard()
    except ImportError:
        click.echo("Error: Dashboard requires 'textual' package.", err=True)
        click.echo("Install with: pip install textual", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
