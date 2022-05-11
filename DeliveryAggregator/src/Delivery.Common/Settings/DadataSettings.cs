namespace Delivery.Common.Settings;

public record DadataSettings
{
    public string Secret { get; set; }
    
    public string Token { get; set; }
}