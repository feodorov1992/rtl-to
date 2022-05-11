namespace Delivery.SDEK.Models;

public record AuthModel
{
    public string AccessToken { get; init; }
    
    public string TokenType { get; init; }
    
    public int ExpiresIn { get; init; }
}