import unidecode

class Track:
    """Track represents a piece of music."""

    def __init__(self, name, artist, album, id=None):
        """
        :param name (str): Track name
        :param id (int): Spotify track id
        :param artist (str): Artist who created the track
        """
        self.name = name
        self.id = id
        self.artist = artist
        self.album = album

    def create_spotify_uri(self):
        return f"spotify:track:{self.id}"

    def __str__(self):
        return self.name + " by " + self.artist
    
    def __repr__(self):
        return self.name + " by " + self.artist
    
    def __eq__(self, o):
        return (uniform_text(self.name) in uniform_text(o.name) or uniform_text(o.name) in uniform_text(self.name)) and (uniform_text(self.artist) in uniform_text(o.artist) or uniform_text(o.artist) in uniform_text(self.artist))
    
def uniform_text(text):
    return unidecode.unidecode(text.lower()).replace("'",'')