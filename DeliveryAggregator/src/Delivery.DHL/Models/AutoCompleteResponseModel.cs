namespace Delivery.DHL.Models;

public record AutoCompleteResponseModel
{
    public ErrorModel[] Errors { get; init; }
    
    public AutoCompleteItemModel[] Success { get; init; }
}