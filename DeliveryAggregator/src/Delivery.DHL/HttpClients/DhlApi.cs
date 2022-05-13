namespace Delivery.DHL.HttpClients;

public class DhlApi
{
    public string Base => "api";

    public string AutoComplete => $"{Base}/autocomplete";

    public string Calculate => $"{Base}/calculateprice";
}