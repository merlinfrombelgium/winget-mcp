namespace WinGetMcpServer.Models;

/// <summary>
/// Error categories for structured exception handling
/// </summary>
public enum ErrorCategory
{
    Validation,
    WinGetOperation,
    SystemError,
    NetworkError,
    SecurityError,
    ConfigurationError
}

/// <summary>
/// Base exception for WinGet MCP Server operations
/// </summary>
public abstract class WinGetMcpException : Exception
{
    public ErrorCategory Category { get; }
    public string UserMessage { get; }
    public Dictionary<string, object> Context { get; }

    protected WinGetMcpException(ErrorCategory category, string userMessage, string technicalMessage, Exception? innerException = null)
        : base(technicalMessage, innerException)
    {
        Category = category;
        UserMessage = userMessage;
        Context = new Dictionary<string, object>();
    }
}

/// <summary>
/// Exception for input validation errors
/// </summary>
public class ValidationException : WinGetMcpException
{
    public ValidationException(string field, string userMessage, string technicalMessage)
        : base(ErrorCategory.Validation, userMessage, technicalMessage)
    {
        Context["Field"] = field;
    }
}

/// <summary>
/// Exception for WinGet operation failures
/// </summary>
public class WinGetOperationException : WinGetMcpException
{
    public WinGetOperationException(string operation, string userMessage, string technicalMessage, Exception? innerException = null)
        : base(ErrorCategory.WinGetOperation, userMessage, technicalMessage, innerException)
    {
        Context["Operation"] = operation;
    }
}

/// <summary>
/// Exception for system-level errors
/// </summary>
public class SystemException : WinGetMcpException
{
    public SystemException(string userMessage, string technicalMessage, Exception? innerException = null)
        : base(ErrorCategory.SystemError, userMessage, technicalMessage, innerException)
    {
    }
}

/// <summary>
/// Exception for security-related errors
/// </summary>
public class SecurityException : WinGetMcpException
{
    public SecurityException(string userMessage, string technicalMessage, Exception? innerException = null)
        : base(ErrorCategory.SecurityError, userMessage, technicalMessage, innerException)
    {
    }
} 