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

var workplace = "Burger King";
var outputFileName = "vagter.json";
var prettyWrite = true;
var shiftOutputFileName = "vagter.txt";

Console.WriteLine("mapsTimelineWork by NJK");

string filePath = @"SemanticLocationHistory/2021/2021_DECEMBER.json";
if(!File.Exists(filePath)) {
  Console.WriteLine($"File '{filePath}' does not exist.");
  Environment.Exit(1);
}

FileStream myStream = File.Open(filePath, FileMode.Open);

var root = JsonSerializer.Deserialize<Root>(myStream);

if (root is null || root.timelineObjects is null) {
  Console.WriteLine("Could not deserialize json file.");
  Environment.Exit(1);
}

root.timelineObjects.RemoveAll(x => x.placeVisit == null);
List<TimelineObject> burgerKingVisits = root.timelineObjects.ToList<TimelineObject>();
burgerKingVisits.RemoveAll(x => x.placeVisit!.location!.name != workplace);

// write the timelineobjects that represent
// my shift. it is written in pretty json
JsonSerializerOptions myOptions = new JsonSerializerOptions() {
  WriteIndented=prettyWrite
};

File.WriteAllText(outputFileName, JsonSerializer.Serialize(burgerKingVisits, myOptions));

// write shifts
List<string> shifts = new List<string>();
int sum = 0;
for (int i = 0; i < burgerKingVisits.Count; i++)
{
  PlaceVisit visit = burgerKingVisits[i].placeVisit!;
  string start = visit.duration!.startTimestamp!;
  DateTime startDate = Convert.ToDateTime(start);
  string end = visit.duration!.endTimestamp!;
  DateTime endDate = Convert.ToDateTime(end);

  TimeSpan shiftDuration = endDate.Subtract(startDate);
  sum += shiftDuration.Hours;

  string day = $"{startDate:dd dddd}";

  string shiftString = $"{day}: {startDate:T} -> {endDate:T}";
  shifts.Add(shiftString);
}

File.WriteAllLines(shiftOutputFileName, shifts);
Console.WriteLine($"You worked {sum} hours.");

Console.WriteLine("Done!");
