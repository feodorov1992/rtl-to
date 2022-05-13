using Delivery.PEK.Models;

namespace Delivery.PEK.Base;

public interface IPekCalcClient
{
    Task<PriceDeliveryResponseModel> Calculate(IReadOnlyList<PriceDeliveryRequestModel> packages, PekRegion from, PekRegion to);
}