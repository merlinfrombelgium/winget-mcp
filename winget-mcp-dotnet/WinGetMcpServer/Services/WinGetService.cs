using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Caching.Memory;
using WinGetMcpServer.Models;
using System.Diagnostics;
using System.Text.Json;

namespace WinGetMcpServer.Services;

/// <summary>
/// Command-line implementation of WinGet operations
/// </summary>
public class WinGetService : IWinGetService
{
    private readonly ILogger<WinGetService> _logger;
    private readonly IMemoryCache _cache;
    private readonly SemaphoreSlim _concurrencyLimiter;

    public WinGetService(ILogger<WinGetService> logger, IMemoryCache cache)
    {
        _logger = logger;
        _cache = cache;
        _concurrencyLimiter = new SemaphoreSlim(Environment.ProcessorCount, Environment.ProcessorCount);
    }

    public async Task<SearchResult> SearchPackagesAsync(string query, int maxResults = 10, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(query))
            throw new ValidationException(nameof(query), "Search query cannot be empty", "Query parameter is null or whitespace");

        var stopwatch = Stopwatch.StartNew();
        var cacheKey = $"search:{query.ToLowerInvariant()}:{maxResults}";
        
        // Check cache first
        if (_cache.TryGetValue(cacheKey, out SearchResult? cachedResult))
        {
            _logger.LogDebug("Cache hit for search query: {Query}", query);
            return cachedResult!;
        }

        await _concurrencyLimiter.WaitAsync(cancellationToken);
        try
        {
            _logger.LogInformation("Searching packages for query: {Query}", query);

            // Execute winget search command
            var arguments = $"search \"{query}\" -n {maxResults} --accept-source-agreements";
            var result = await ExecuteWinGetCommandAsync(arguments, cancellationToken);

            if (!result.Success)
            {
                throw new WinGetOperationException("search", 
                    $"Search failed for query '{query}'", 
                    $"WinGet command failed with exit code {result.ExitCode}: {result.ErrorOutput}");
            }

            // Parse the search results
            _logger.LogDebug("WinGet search output: {Output}", result.Output);
            var packages = ParseSearchOutput(result.Output, maxResults);

            stopwatch.Stop();
            var searchResult = new SearchResult
            {
                Query = query,
                Packages = packages,
                TotalFound = packages.Count,
                Returned = packages.Count,
                ExecutionTime = stopwatch.Elapsed,
                HasMore = packages.Count >= maxResults,
                Source = "winget"
            };

            // Cache the result
            var cacheOptions = new MemoryCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5),
                SlidingExpiration = TimeSpan.FromMinutes(2),
                Priority = CacheItemPriority.Normal
            };
            _cache.Set(cacheKey, searchResult, cacheOptions);

            _logger.LogInformation("Search completed for query: {Query}, found {Count} packages in {ElapsedMs}ms", 
                query, packages.Count, stopwatch.ElapsedMilliseconds);

            return searchResult;
        }
        catch (Exception ex) when (!(ex is WinGetMcpException))
        {
            _logger.LogError(ex, "Failed to search packages for query: {Query}", query);
            throw new WinGetOperationException("search", 
                $"Search failed for query '{query}'", 
                $"Package search operation failed: {ex.Message}", ex);
        }
        finally
        {
            _concurrencyLimiter.Release();
        }
    }

    public async Task<PackageInfo?> GetPackageInfoAsync(string packageId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(packageId))
            throw new ValidationException(nameof(packageId), "Package ID cannot be empty", "PackageId parameter is null or whitespace");

        _logger.LogInformation("Getting package info for: {PackageId}", packageId);

        try
        {
            // Use search to find the specific package
            var searchResult = await SearchPackagesAsync(packageId, 1, cancellationToken);
            return searchResult.Packages.FirstOrDefault(p => p.Id.Equals(packageId, StringComparison.OrdinalIgnoreCase));
        }
        catch (Exception ex) when (!(ex is WinGetMcpException))
        {
            _logger.LogError(ex, "Failed to get package info for: {PackageId}", packageId);
            throw new WinGetOperationException("info", 
                $"Failed to get information for package '{packageId}'", 
                $"Package info operation failed: {ex.Message}", ex);
        }
    }

    public async Task<List<PackageInfo>> ListInstalledPackagesAsync(int maxResults = 20, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Listing installed packages (max: {MaxResults})", maxResults);

        try
        {
            var arguments = $"list --accept-source-agreements";
            var result = await ExecuteWinGetCommandAsync(arguments, cancellationToken);

            if (!result.Success)
            {
                throw new WinGetOperationException("list", 
                    "Failed to list installed packages", 
                    $"WinGet command failed with exit code {result.ExitCode}: {result.ErrorOutput}");
            }

            var packages = ParseListOutput(result.Output, maxResults);
            return packages;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to list installed packages");
            throw new WinGetOperationException("list", 
                "Failed to list installed packages", 
                $"List packages operation failed: {ex.Message}", ex);
        }
    }

    public async Task<InstallResult> InstallPackageAsync(string packageId, string? version = null, bool silent = true, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(packageId))
            throw new ValidationException(nameof(packageId), "Package ID cannot be empty", "PackageId parameter is null or whitespace");

        _logger.LogWarning("Package installation is disabled in this implementation for security reasons");
        
        // For security, we'll return a simulated result
        await Task.Delay(100, cancellationToken);
        
        return new InstallResult
        {
            PackageId = packageId,
            Version = version,
            Success = false,
            ErrorMessage = "Package installation is disabled for security reasons",
            ExitCode = -1,
            ExecutionTime = TimeSpan.FromMilliseconds(100),
            RequiredRestart = false
        };
    }

    public async Task<bool> IsAvailableAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            // Test if winget is available by running a simple command
            var result = await ExecuteWinGetCommandAsync("--version", cancellationToken);
            return result.Success;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "WinGet is not available");
            return false;
        }
    }

    private async Task<(bool Success, string Output, string ErrorOutput, int ExitCode)> ExecuteWinGetCommandAsync(string arguments, CancellationToken cancellationToken)
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = "winget",
            Arguments = arguments,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
            StandardOutputEncoding = System.Text.Encoding.UTF8,
            StandardErrorEncoding = System.Text.Encoding.UTF8
        };

        using var process = new Process { StartInfo = startInfo };
        var outputBuilder = new System.Text.StringBuilder();
        var errorBuilder = new System.Text.StringBuilder();

        process.OutputDataReceived += (sender, e) => 
        {
            if (e.Data != null) outputBuilder.AppendLine(e.Data);
        };
        process.ErrorDataReceived += (sender, e) => 
        {
            if (e.Data != null) errorBuilder.AppendLine(e.Data);
        };

        process.Start();
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();

        await process.WaitForExitAsync(cancellationToken);

        return (process.ExitCode == 0, outputBuilder.ToString(), errorBuilder.ToString(), process.ExitCode);
    }

    private List<PackageInfo> ParseSearchOutput(string output, int maxResults)
    {
        var packages = new List<PackageInfo>();
        var lines = output.Split('\n', StringSplitOptions.RemoveEmptyEntries);

        // Skip header lines and parse package information
        foreach (var line in lines.Skip(2).Take(maxResults)) // Skip first 2 lines (header)
        {
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("-")) continue;

            // Parse winget search output format (space-separated with fixed columns)
            // Format: Name                   Id           Version Source
            var parts = line.Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length >= 4)
            {
                // Find where ID starts (first part that looks like an ID)
                int idIndex = 1;
                while (idIndex < parts.Length && !IsLikelyPackageId(parts[idIndex]))
                {
                    idIndex++;
                }

                if (idIndex < parts.Length)
                {
                    var name = string.Join(" ", parts.Take(idIndex));
                    var id = parts[idIndex];
                    var version = parts.Length > idIndex + 1 ? parts[idIndex + 1] : "Unknown";
                    var source = parts.Length > idIndex + 2 ? parts[idIndex + 2] : "winget";

                    packages.Add(new PackageInfo
                    {
                        Id = id.Trim(),
                        Name = name.Trim(),
                        Version = version.Trim(),
                        Publisher = "Unknown",
                        Description = "",
                        Source = source.Trim(),
                        IsInstalled = false
                    });
                }
            }
        }

        return packages;
    }

    private bool IsLikelyPackageId(string text)
    {
        // Package IDs typically contain dots, numbers, or are all caps
        return text.Contains('.') || text.Contains('_') || text.All(char.IsUpper) || 
               (text.Length > 8 && text.Any(char.IsDigit));
    }

    private List<PackageInfo> ParseListOutput(string output, int maxResults)
    {
        var packages = new List<PackageInfo>();
        var lines = output.Split('\n', StringSplitOptions.RemoveEmptyEntries);

        // Skip header lines and parse package information
        foreach (var line in lines.Skip(2).Take(maxResults)) // Skip first 2 lines (header)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;

            // Parse winget list output format
            var parts = line.Split('\t', StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length >= 3)
            {
                packages.Add(new PackageInfo
                {
                    Id = parts[0].Trim(),
                    Name = parts[1].Trim(),
                    Version = parts[2].Trim(),
                    Publisher = parts.Length > 3 ? parts[3].Trim() : "Unknown",
                    Description = "",
                    Source = "winget",
                    IsInstalled = true
                });
            }
        }

        return packages;
    }

    public void Dispose()
    {
        _concurrencyLimiter?.Dispose();
    }
} 