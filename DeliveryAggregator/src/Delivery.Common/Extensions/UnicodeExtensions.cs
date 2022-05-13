using System.Globalization;
using System.Text.RegularExpressions;

namespace Delivery.Common.Extensions;

public static class UnicodeExtensions
{
    private static readonly Regex Regex = new(@"\\[uU]([0-9A-Fa-f]{4})");

    public static string UnescapeUnicode(this string str)
    {
        return Regex.Replace(str, match => ((char)int.Parse(match.Value.Substring(2), NumberStyles.HexNumber)).ToString());
    }
}