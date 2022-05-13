using AutoMapper;
using Delivery.Common.Exceptions;
using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;
using Delivery.Common.ServicesBase;
using Delivery.DHL.Base;
using Delivery.DHL.Models;

namespace Delivery.DHL.Services;

public class DeliveryPricingService : IDeliveryPricingService
{
    private readonly IDhlClient _dhlClient;
    private readonly ICityResolveService _cityResolveService;
    private readonly IMapper _mapper;

    public DeliveryPricingService(IDhlClient dhlClient, ICityResolveService cityResolveService, IMapper mapper)
    {
        _dhlClient = dhlClient;
        _cityResolveService = cityResolveService;
        _mapper = mapper;
    }
    
    public async Task<IReadOnlyCollection<DeliveryPricingResult>> GetDeliveryPrices(DeliveryPricingRequest request, 
        AddressShortModel from, 
        AddressShortModel to)
    {
        if (from is null)
            throw new CounterpartyClientException("From address is not resolved");
        
        if (to is null)
            throw new CounterpartyClientException("To address is not resolved");
        
        var resolvedFrom = await _cityResolveService.GetCityId(from.PostalCode);
        if (resolvedFrom is null)
            throw new CounterpartyClientException("Couldn't resolve From address");
        
        var resolvedTo = await _cityResolveService.GetCityId(to.PostalCode);
        if (resolvedTo is null)
            throw new CounterpartyClientException("Couldn't resolve To address");
        
        var dhlRequest = _mapper.Map<CalculatePriceRequestModel>(request);
        dhlRequest = dhlRequest with
        {
            CityFrom = resolvedFrom,
            CityTo = resolvedTo,
            PostalCodeFrom = from.PostalCode,
            PostalCodeTo = to.PostalCode
        };

        var response = await _dhlClient.Calculate(dhlRequest);
        if (response is null)
            throw new CounterpartyClientException("Unexpected error");

        if (response.Errors?.Any() == true)
            throw new CounterpartyClientException(string.Join(Environment.NewLine, response.Errors.Select(x => x.Message)));
        
        if (response.Success is null)
            throw new CounterpartyClientException("Unexpected error");

        var walkItem = _mapper.Map<DeliveryPricingResult>(response.Success.Walk);
        walkItem = walkItem with { CounterpartyId = "walk" };

        var clickItem = _mapper.Map<DeliveryPricingResult>(response.Success.Click);
        clickItem = clickItem with { CounterpartyId = "click" };

        var callItem = _mapper.Map<DeliveryPricingResult>(response.Success.Call);
        callItem = callItem with { CounterpartyId = "call" };

        return new[] { walkItem, clickItem, callItem };
    }
}