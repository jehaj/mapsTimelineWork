/* 
  Dette program bruges til at gå igennem data fra Google Tidslinje. 
  Dataen er fået gennem Google Takeout.

  Det kan f.eks. bruges til at se hvor lang tid du har været på 
  arbejde eller i skole. I tilfældet med arbejde kan man undersøge 
  om lønnen stemmer overens.

  Dette er kun tænkte eksempler og programmet udvikles udelukkende 
  for lærings skyld.

  NJK
 */

using System.Text.Json;

Console.WriteLine("mapsTimelineWork");

string filePath = @"/home/nikolaj/Documents/Google-Project/Takeout/Lokationshistorik/Semantic Location History/2021/2021_DECEMBER.json";
string jsonString = File.ReadAllText(filePath);

string locationName = "Burger King";

string basePath = @"/home/nikolaj/Documents/Google-Project/Takeout/Lokationshistorik/Semantic Location History/";
Dictionary<string, int> folders = new Dictionary<string, int>() {
  {"2020", 12},
  {"2021", 12},
  {"2022", 0}
};
string[] months = new string[] {
  "_JANUARY",
  "_FEBRUARY",
  "_MARCH",
  "_APRIL",
  "_MAY",
  "_JUNE",
  "_JULY",
  "_AUGUST",
  "_SEPTEMBER",
  "_OCTOBER",
  "_NOVEMBER",
  "_DECEMBER",
};

List<string> filePaths = new List<string>();

foreach (var key in folders.Keys)
{
    for (int j = 0; j < folders[key]; j++)
    {
        filePaths.Add(Path.Combine(basePath, key, key + months[j] + ".json"));
    }
}

List<TimelineObject> workplaceVisits = new List<TimelineObject>();

for (int i = 0; i < filePaths.Count; i++)
{
    FileStream myStream = File.Open(filePaths[i], FileMode.Open);

    var root = JsonSerializer.Deserialize<Root>(myStream);
    myStream.Close();

    if (root == null)
    {
      Console.WriteLine("Der er problemer med JSON-filen :c");
      Environment.Exit(1);
    }

    root.timelineObjects.RemoveAll(x => x.placeVisit == null);
    root.timelineObjects.RemoveAll(x => x.placeVisit.location.name != "Burger King");
    workplaceVisits.AddRange(root.timelineObjects.ToList<TimelineObject>());
}

// Skriv vagter til tekst-fil
List<string> textOutput = new List<string>();

for (int i = 0; i < workplaceVisits.Count; i++)
{
    DateTime start = DateTimeOffset.FromUnixTimeMilliseconds(long.Parse(workplaceVisits[i].placeVisit.duration.startTimestampMs)).DateTime;
    DateTime end = DateTimeOffset.FromUnixTimeMilliseconds(long.Parse(workplaceVisits[i].placeVisit.duration.endTimestampMs)).DateTime;
    string output = $"{start,-10:dddd}{start: dd/MM HH.mm.ss} -> {end:HH.mm.ss}";
    textOutput.Add(output);
    
}

File.WriteAllLines("vagter.txt", textOutput);

Console.WriteLine($"Du har været ved {locationName} {workplaceVisits.Count} gange.");
Console.WriteLine("Check vagter.txt for mere information.");

Console.WriteLine("Done");
