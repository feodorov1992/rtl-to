namespace Delivery.SDEK.Settings;

public record ApiSettings
{
    public string BaseUrl { get; init; }
    public string Account { get; init; }
    public string Password { get; init; }
}