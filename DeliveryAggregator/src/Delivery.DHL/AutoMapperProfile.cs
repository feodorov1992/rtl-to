using AutoMapper;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;
using Delivery.DHL.Models;

namespace Delivery.DHL;

public class AutoMapperProfile : Profile
{
    public AutoMapperProfile()
    {
        CreateMap<DeliveryPricingRequest, CalculatePriceRequestModel>()
            .ForMember(x => x.CountryCodeFrom, opt => opt.MapFrom(src => "RU"))
            .ForMember(x => x.CountryCodeTo, opt => opt.MapFrom(src => "RU"))
            .ForMember(x => x.Pieces, opt => opt.MapFrom(src => Enumerable.Range(0, src.Quantity)
                .Select(x => new DeliveryPieceModel
                {
                    Id = x,
                    Weight = src.Weight,
                    Type = 1,
                    Width = src.Width,
                    Height = src.Height,
                    Depth = src.Length
                })
                .ToArray()))
            .ForMember(x => x.Date, opt => opt.MapFrom(_ => DateTime.UtcNow.Date.ToString("yyyy-MM-dd")))
            .ForMember(x => x.PickUpFromTime, opt => opt.MapFrom(_ => "9:00"))
            .ForMember(x => x.ShpWindowsTimeZoneId, opt => opt.MapFrom(_ => "Russia Time Zone 3"))
            .ForMember(x => x.OfficeRoute, opt => opt.MapFrom(_ => "SAS0"))
            .ForMember(x => x.Language, opt => opt.MapFrom(_ => "ru"));

        CreateMap<CalculatePriceElementModel, DeliveryPricingResult>()
            .ForMember(x => x.Price, opt => opt.MapFrom(src => src.Price))
            .ForMember(x => x.MinTime, opt => opt.MapFrom(src => src.TotalTransitDays))
            .ForMember(x => x.MaxTime, opt => opt.MapFrom(src => src.TotalTransitDays));
    }
}