using Delivery.DHL.Models;

namespace Delivery.DHL.Base;

public interface IDhlClient
{
    Task<AutoCompleteResponseModel> ResolveCity(AutoCompleteRequestModel request);
    Task<CalculatePriceResponseModel> Calculate(CalculatePriceRequestModel request);
}