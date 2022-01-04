public class Location
{
    public int latitudeE7 { get; set; }
    public int longitudeE7 { get; set; }
    public string? name { get; set; }
}

public class Duration
{
    public string? startTimestampMs { get; set; }
    public string? endTimestampMs { get; set; }
}

public class PlaceVisit
{
    public Location? location { get; set; }
    public Duration? duration { get; set; }
}

public class TimelineObject
{
    public PlaceVisit? placeVisit { get; set; }
}

public class Root
{
    public List<TimelineObject>? timelineObjects { get; set; }
}
