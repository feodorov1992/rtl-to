using Delivery.PEK.Models;

namespace Delivery.PEK.Base;

public interface IPekTownsClient
{
    Task<IReadOnlyCollection<PekTown>> GetTowns();
}