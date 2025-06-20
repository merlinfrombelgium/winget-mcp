namespace WinGetMcpServer.Configuration;

/// <summary>
/// Configuration options for the MCP server
/// </summary>
public class McpServerOptions
{
    public const string SectionName = "McpServer";

    public string ServerName { get; set; } = "WinGet MCP Server";
    public string Version { get; set; } = "1.0.0";
    public bool EnableInstallOperations { get; set; } = false;
    public CacheOptions Cache { get; set; } = new();
    public SecurityOptions Security { get; set; } = new();
    public PerformanceOptions Performance { get; set; } = new();
}

/// <summary>
/// Cache configuration options
/// </summary>
public class CacheOptions
{
    public bool Enabled { get; set; } = true;
    public int DefaultExpirationMinutes { get; set; } = 5;
    public int SlidingExpirationMinutes { get; set; } = 2;
    public int MaxCacheSize { get; set; } = 1000;
}

/// <summary>
/// Security configuration options
/// </summary>
public class SecurityOptions
{
    public int MaxQueryLength { get; set; } = 256;
    public int MaxResultsPerQuery { get; set; } = 50;
    public bool EnableInputSanitization { get; set; } = true;
    public bool LogSecurityEvents { get; set; } = true;
    public string[] AllowedSources { get; set; } = { "winget", "msstore" };
}

/// <summary>
/// Performance configuration options
/// </summary>
public class PerformanceOptions
{
    public int MaxConcurrentOperations { get; set; } = Environment.ProcessorCount;
    public int DefaultTimeoutSeconds { get; set; } = 30;
    public bool EnablePerformanceLogging { get; set; } = true;
} 