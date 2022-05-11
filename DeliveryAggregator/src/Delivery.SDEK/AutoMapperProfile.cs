using System.Net.Sockets;
using AutoMapper;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;
using Delivery.SDEK.Models;

namespace Delivery.SDEK;

public class AutoMapperProfile : Profile
{
    public AutoMapperProfile()
    {
        CreateMap<DeliveryPricingRequest, TariffListRequestModel>()
            .ForMember(x => x.FromLocation, opt => opt.MapFrom(src => new SdekLocation
            {
                Address = src.FromAddress
            }))
            .ForMember(x => x.ToLocation, opt => opt.MapFrom(src => new SdekLocation
            {
                Address = src.ToAddress
            }))
            .ForMember(x => x.Packages, opt => opt.MapFrom(src =>
                Enumerable.Range(1, src.Quantity).Select(_ =>
                    new SdekPackage
                    {
                        Weight = (int)src.Weight,
                        Length = (int)src.Length,
                        Width = (int)src.Width,
                        Height = (int)src.Height
                    }).ToArray()
            ));

        CreateMap<TariffCodeModel, DeliveryPricingResult>()
            .ForMember(x => x.CounterpartyId, opt => opt.MapFrom(src => src.TariffCode))
            .ForMember(x => x.MinTime, opt => opt.MapFrom(src => src.PeriodMin))
            .ForMember(x => x.MaxTime, opt => opt.MapFrom(src => src.PeriodMax))
            .ForMember(x => x.Price, opt => opt.MapFrom(src => src.DeliverySum));
    }
}