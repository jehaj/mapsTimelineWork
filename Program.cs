/* 
  Dette program bruges til at gå igennem
  data fra Google Tidslinje. Dataen er 
  fået gennem Google Takeout.

  Det kan f.eks. bruges til at se hvor
  lang tid du har været på arbejde eller
  i skole. I tilfældet med arbejde kan
  man undersøge om lønnen stemmer overens.

  Dette er kun tænkte eksempler og programmet
  udvikles udelukkende for lærings skyld.

  NJK
 */

using System.Text.Json;

Console.WriteLine("mapsTimelineWork");

string filePath = @"/home/nikolaj/Documents/Google-Project/Takeout/Lokationshistorik/Semantic Location History/2021/2021_DECEMBER.json";
string jsonString = File.ReadAllText(filePath);

FileStream myStream = File.Open(filePath, FileMode.Open);

var root = JsonSerializer.Deserialize<Root>(myStream);

if (root == null)
{
  Console.WriteLine("Der er problemer med JSON-filen :c");
  Environment.Exit(1);
}

root.timelineObjects.RemoveAll(x => x.placeVisit == null);
List<TimelineObject> burgerKingVisits = root.timelineObjects.ToList<TimelineObject>();
burgerKingVisits.RemoveAll(x => x.placeVisit.location.name != "Burger King");



Console.WriteLine("Done");
