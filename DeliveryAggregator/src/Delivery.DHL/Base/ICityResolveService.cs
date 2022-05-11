namespace Delivery.DHL.Base;

public interface ICityResolveService
{
    Task<string> GetCityId(string postalCode);
}