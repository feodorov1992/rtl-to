using AutoMapper;
using Dadata.Model;
using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Responses.DeliveryPricing;

namespace Delivery.Common;

public sealed class CommonAssemblyProfile : Profile
{
    public CommonAssemblyProfile()
    {
        CreateMap<DeliveryPricingResult, DeliveryPricingResponse>();
        CreateMap<Address, AddressShortModel>()
            .ForMember(x => x.FormattedAddress, x => x.MapFrom(src => src.result))
            .ForMember(x => x.Country, x => x.MapFrom(src => src.country))
            .ForMember(x => x.Region, x => x.MapFrom(src => src.region))
            .ForMember(x => x.City, x => x.MapFrom(src => src.settlement ?? src.city ?? src.region))
            .ForMember(x => x.Street, x => x.MapFrom(src => src.street))
            .ForMember(x => x.House, x => x.MapFrom(src => src.house))
            .ForMember(x => x.Flat, x => x.MapFrom(src => src.flat))
            .ForMember(x => x.KladrId, x => x.MapFrom(src => src.kladr_id))
            .ForMember(x => x.CountryCodeIso, x => x.MapFrom(src => src.country_iso_code))
            .ForMember(x => x.District, x => x.MapFrom(src => src.city_district ?? src.area))
            .ForMember(x => x.PostalCode, x => x.MapFrom(src => src.postal_code));
    }
}