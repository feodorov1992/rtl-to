using System.Reflection;
using System.Text;
using Delivery.PEK.Base;
using Delivery.PEK.Models;
using TinyCsvParser;

namespace Delivery.PEK.Services;

public class RegionsRepository : IRegionsRepository
{
    public async Task<IReadOnlyCollection<GeoRegion>> GetAll()
    {
        var parserOptions = new CsvParserOptions(true, ',');
        var mapping = new GetRegionMapping();
        var parser = new CsvParser<GeoRegion>(parserOptions, mapping);
        
        var assembly = Assembly.GetExecutingAssembly();
        var resourceName = "Delivery.PEK.regions.csv";

        await using (Stream stream = assembly.GetManifestResourceStream(resourceName))
        {
            var items = parser.ReadFromStream(stream, Encoding.UTF8);
            return items.Select(x => x.Result).ToList();
        }
    }

    public async Task<GeoRegion> GetByRegionName(string regionName)
    {
        var allRegions = await GetAll();
        return allRegions.FirstOrDefault(x => x.Name.Equals(regionName, StringComparison.InvariantCultureIgnoreCase));
    }
}