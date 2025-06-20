namespace WinGetMcpServer.Models;

/// <summary>
/// Represents the result of a package search operation
/// </summary>
public class SearchResult
{
    public required string Query { get; set; }
    public required List<PackageInfo> Packages { get; set; }
    public int TotalFound { get; set; }
    public int Returned { get; set; }
    public TimeSpan ExecutionTime { get; set; }
    public bool HasMore { get; set; }
    public string? Source { get; set; }
} 