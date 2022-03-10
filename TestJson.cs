using System.Text.Json;

public class TestJson
{
    static void JsonTest()
    {
        string outPath = @"/home/nikolaj/Documents/Google-Project/Takeout/Lokationshistorik/Semantic Location History/2021/out.json";

        var placeVisit1 = new PlaceVisit
        {
            location = new Location { latitudeE7 = 1, longitudeE7 = 2, name = "bebo" },
            duration = new Duration { startTimestamp = "5", endTimestamp = "10" }
        };
        var placeVisit2 = new PlaceVisit
        {
            location = new Location { latitudeE7 = 7, longitudeE7 = 0, name = "moob" },
            duration = new Duration { startTimestamp = "9", endTimestamp = "101" }
        };

        var timelineObjects = new Root
        {
            timelineObjects = new List<TimelineObject> {
        new TimelineObject { placeVisit = placeVisit1 },
        new TimelineObject { placeVisit = placeVisit2 }
    }
        };

        JsonSerializerOptions options = new JsonSerializerOptions
        {
            WriteIndented = true
        };

        Console.WriteLine(JsonSerializer.Serialize<Root>(timelineObjects, options));
        File.WriteAllText(outPath, JsonSerializer.Serialize(timelineObjects, options));
    }

}

