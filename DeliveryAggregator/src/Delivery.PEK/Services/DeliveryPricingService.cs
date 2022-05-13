using AutoMapper;
using Delivery.Common.Exceptions;
using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;
using Delivery.Common.ServicesBase;
using Delivery.PEK.Base;
using Delivery.PEK.Models;

namespace Delivery.PEK.Services;

public class DeliveryPricingService : IDeliveryPricingService
{
    private readonly ITownsRepository _townsRepository;
    private readonly IPekCalcClient _calcClient;
    private readonly IMapper _mapper;

    public DeliveryPricingService(ITownsRepository townsRepository, IPekCalcClient calcClient, IMapper mapper)
    {
        _townsRepository = townsRepository;
        _calcClient = calcClient;
        _mapper = mapper;
    }
    
    public async Task<IReadOnlyCollection<DeliveryPricingResult>> GetDeliveryPrices(DeliveryPricingRequest request, 
        AddressShortModel from, 
        AddressShortModel to)
    {
        var fromTown = await _townsRepository.GetTown(from);
        if (fromTown is null)
            throw new CounterpartyClientException($"Couldn't resolve address: {from.FormattedAddress}");
        
        var toTown = await _townsRepository.GetTown(to);
        if (toTown is null)
            throw new CounterpartyClientException($"Couldn't resolve address: {to.FormattedAddress}");

        var pekRequest = Enumerable.Range(1, request.Quantity).Select(_ => _mapper.Map<PriceDeliveryRequestModel>(request)).ToList();
        
        var response = await _calcClient.Calculate(pekRequest, fromTown, toTown);
        if (response is null || (response.Avia is null && response.Auto is null))
        {
            ProcessDeliveryPriceError(response);
            return null;
        }

        var minDays = 0;
        var maxDays = 0;
        
        var periods = response.PeriodsDays.Split(" - ", StringSplitOptions.RemoveEmptyEntries);
        if (periods.Length == 2)
        {
            minDays = Convert.ToInt32(periods[0]);
            maxDays = Convert.ToInt32(periods[1]);
        }

        var result = new List<DeliveryPricingResult>();

        var takePrice = response.Take is not null ? Convert.ToDecimal(response.Take[2]) : 0;
        var deliveryPrice = response.Delivery is not null ? Convert.ToDecimal(response.Delivery[2]) : 0;

        var additionalPrices = new[]
            {
                response.Add,
                response.Add1,
                response.Add2,
                response.Add3,
                response.Add4,
            }.Where(x => x is not null)
            .Sum(x => Convert.ToDecimal(x["3"]));

        if (response.Auto is not null)
        {
            var autoPrice = Convert.ToDecimal(response.Auto[2]);            
            
            var autoResult = new DeliveryPricingResult
            {
                CounterpartyId = "auto",
                MinTime = minDays,
                MaxTime = maxDays,
                Price = takePrice + autoPrice + deliveryPrice + additionalPrices
            };

            result.Add(autoResult);
        }

        if (response.Avia is not null)
        {
            var aviaPrice = Convert.ToDecimal(response.Avia[2]);
            
            var aviaResult = new DeliveryPricingResult
            {
                CounterpartyId = "avia",
                MinTime = minDays,
                MaxTime = maxDays,
                Price = takePrice + aviaPrice + deliveryPrice + additionalPrices
            };
            
            result.Add(aviaResult);
        }

        return result;
    }
    
    private void ProcessDeliveryPriceError(PriceDeliveryResponseModel response)
    {
        throw new CounterpartyClientException(string.Join(";", response.Error));
    }
}