using TinyCsvParser.Mapping;

namespace Delivery.PEK.Models;

public class GetRegionMapping : CsvMapping<GeoRegion>
{
    public GetRegionMapping()
    {
        MapProperty(0, x => x.Name);
        MapProperty(1, x => x.Type);
        MapProperty(2, x => x.Capital);
    }
}