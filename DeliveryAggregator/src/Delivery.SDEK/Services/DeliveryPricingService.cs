using System.Net;
using AutoMapper;
using Delivery.Common.Exceptions;
using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;
using Delivery.Common.ServicesBase;
using Delivery.SDEK.Base;
using Delivery.SDEK.Models;

namespace Delivery.SDEK.Services;

public class DeliveryPricingService : IDeliveryPricingService
{
    private readonly ISdekClient _sdekClient;
    private readonly IMapper _mapper;

    public DeliveryPricingService(ISdekClient sdekClient, IMapper mapper)
    {
        _sdekClient = sdekClient;
        _mapper = mapper;
    }
    
    public async Task<IReadOnlyCollection<DeliveryPricingResult>> GetDeliveryPrices(DeliveryPricingRequest request,
        AddressShortModel from, 
        AddressShortModel to)
    {
        var sdekRequest = _mapper.Map<TariffListRequestModel>(request);

        if (from is not null)
        {
            sdekRequest = sdekRequest with
            {
                FromLocation = new SdekLocation
                {
                    CountryCode = from.CountryCodeIso,
                    City = from.City,
                    Address = from.FormattedAddress
                }
            };
        }

        if (to is not null)
        {
            sdekRequest = sdekRequest with
            {
                ToLocation = new SdekLocation
                {
                    CountryCode = to.CountryCodeIso,
                    City = to.City,
                    Address = to.FormattedAddress
                }
            };
        }

        var response = await _sdekClient.GetPrices(sdekRequest);
        if (response.Errors?.Any() == true)
        {
            ProcessDeliveryPriceError(response);
            return null;
        }

        return _mapper.Map<DeliveryPricingResult[]>(response.TariffCodes);
    }

    private void ProcessDeliveryPriceError(TariffListResponseModel response)
    {
        if (response?.Errors is null)
            throw new CounterpartyClientException("Unexpected error");

        throw new CounterpartyClientException(string.Join(Environment.NewLine, response.Errors.Select(x => x.Message)));
    }
}