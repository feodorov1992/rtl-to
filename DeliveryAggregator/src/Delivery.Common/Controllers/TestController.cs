using Microsoft.AspNetCore.Mvc;

namespace Delivery.Common.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TestController
{
    [HttpGet]
    public ActionResult<string> Test()
    {
        return "Test";
    }
}