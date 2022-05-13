using System.Net;
using AutoMapper;
using Delivery.Common.Exceptions;
using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;
using Delivery.Common.ServicesBase;
using Delivery.Common.Settings;
using Delivery.ZDE.Base;
using Delivery.ZDE.Models;
using Microsoft.Extensions.Options;

namespace Delivery.ZDE.Services;

public class DeliveryPricingService : IDeliveryPricingService
{
    private readonly IZdeClient _zdeClient;
    private readonly IMapper _mapper;

    public DeliveryPricingService(IZdeClient zdeClient, IMapper mapper)
    {
        _zdeClient = zdeClient;
        _mapper = mapper;
    }
    
    public async Task<IReadOnlyCollection<DeliveryPricingResult>> GetDeliveryPrices(DeliveryPricingRequest request, 
        AddressShortModel from, AddressShortModel to)
    {
        var zdeRequest = _mapper.Map<PriceAddressRequestModel>(request);

        var response = await _zdeClient.GetPrice(zdeRequest);
        if (response is null || response.Result == 0)
        {
            ProcessDeliveryPriceError(response);
            return null;
        }

        var service = response.Services.FirstOrDefault();
        if (service is null)
            throw new HttpRequestException("Prices not found", null, HttpStatusCode.NotFound);
        
        if (decimal.TryParse(service.Price, out var price))
        {
            var result = new DeliveryPricingResult
            {
                CounterpartyId = response.Type.ToString(),
                MinTime = response.MinDays,
                MaxTime = response.MaxDays,
                Price = price
            };
            return new[] { result };
        }
        
        throw new CounterpartyClientException("Failed to get Price value from the response");
    }

    private void ProcessDeliveryPriceError(PriceAddressResponseModel response)
    {
        if (response?.Services is null)
            throw new CounterpartyClientException("Unexpected error");

        var service = response.Services.FirstOrDefault();
        if (service is null)
            throw new HttpRequestException("Prices not found", null, HttpStatusCode.NotFound);

        throw new CounterpartyClientException(service.Error);
    }
}