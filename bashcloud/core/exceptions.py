# bashcloud/core/exceptions.py
# -----------------------------
# all custom exceptions definition in one place. This way the CLI can catch
# specific error types and display helpful messages instead of ugly stack traces.
# The hierarchy lets me catch BashCloudError to handle all app errors, or catch
# specific subclasses when finer control is needed.


class BashCloudError(Exception):
    """
    Base exception for all BashCloud errors.
    
    This as the parent class so that CLI entrypoint can catch any
    BashCloud-related error with a single except clause and display it cleanly.
    """
    
    def __init__(self, message, suggestion=None):
        # include an optional suggestion field because many errors have
        # a clear fix the user should try, like "run aws configure"
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
    
    def __str__(self):
        if self.suggestion:
            return f"{self.message}\n  Suggestion: {self.suggestion}"
        return self.message


class CLIUnavailableError(BashCloudError):
    """
    Raised when a required CLI tool is not installed or not in PATH.
    
    For example if someone tries to run AWS cost queries but does not have
    the aws CLI installed,, raises this with instructions on how to install it.
    """
    
    def __init__(self, cli_name, install_instructions=None):
        message = f"The '{cli_name}' CLI is not installed or not in PATH."
        suggestion = install_instructions or f"Install {cli_name} and ensure it is in your PATH."
        super().__init__(message, suggestion)
        self.cli_name = cli_name


class CredentialError(BashCloudError):
    """
    Raised when CLI credentials are missing or invalid.
    
    This happens when aws configure has not been run, or the credentials
    have expired., gives the user clear instructions on how to fix it.
    """
    
    def __init__(self, provider, details=None):
        message = f"Credentials for {provider} are missing or invalid."
        if details:
            message = f"{message} {details}"
        
        suggestions = {
            "aws": "Run 'aws configure' to set up your credentials.",
            "azure": "Run 'az login' to authenticate.",
            "gcp": "Run 'gcloud auth login' to authenticate.",
        }
        suggestion = suggestions.get(provider.lower(), "Configure your cloud credentials.")
        super().__init__(message, suggestion)
        self.provider = provider


class PermissionDeniedError(BashCloudError):
    """
    Raised when the authenticated user lacks required permissions.
    
    For AWS cost queries this usually means the IAM user does not have
    ce:GetCostAndUsage permission., tells them exactly what permission they need.
    """
    
    def __init__(self, provider, required_permission=None, details=None):
        message = f"Permission denied when accessing {provider} resources."
        if details:
            message = f"{message} {details}"
        
        if required_permission:
            suggestion = f"Ensure your user/role has the '{required_permission}' permission."
        else:
            suggestion = "Check that your credentials have the required permissions."
        
        super().__init__(message, suggestion)
        self.provider = provider
        self.required_permission = required_permission


class PaginationError(BashCloudError):
    """
    Raised when pagination fails or enters an infinite loop.
    
    Cloud APIs return next page tokens and if we see the same token twice
    something is wrong., also raises this if we exceed a maximum page count
    to prevent runaway pagination.
    """
    
    def __init__(self, message, token=None):
        suggestion = "This may indicate an API issue. Try narrowing your query date range."
        super().__init__(message, suggestion)
        self.token = token


class ParsingError(BashCloudError):
    """
    Raised when CLI output cannot be parsed as expected.
    
    This happens when the CLI returns malformed JSON or the response schema
    has changed., logs what we received to help with debugging.
    """
    
    def __init__(self, message, raw_output=None):
        suggestion = "The CLI output format may have changed. Check your CLI version."
        super().__init__(message, suggestion)
        self.raw_output = raw_output


class ConfigurationError(BashCloudError):
    """
    Raised when there is a problem with BashCloud configuration.
    
    For example if the config file has invalid syntax or missing required fields.
    """
    
    def __init__(self, message, config_path=None):
        suggestion = "Check your configuration file for syntax errors."
        if config_path:
            suggestion = f"Check {config_path} for syntax errors."
        super().__init__(message, suggestion)
        self.config_path = config_path


class DateRangeError(BashCloudError):
    """
    Raised when date inputs are invalid.
    
    Start date after end date, non-ISO format, future dates beyond what the
    API supports, etc.
    """
    
    def __init__(self, message):
        suggestion = "Use dates in YYYY-MM-DD format with start date before end date."
        super().__init__(message, suggestion)


class ExportError(BashCloudError):
    """
    Raised when exporting results to file fails.
    
    Usually a permissions issue with the output path or disk full.
    """
    
    def __init__(self, message, path=None):
        suggestion = "Check that you have write permissions to the output directory."
        super().__init__(message, suggestion)
        self.path = path
