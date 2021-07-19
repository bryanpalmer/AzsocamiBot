class Embed:
    def __init__(self):
        # title values
        self.title = ""
        self.titleUrl = ""
        self.titleDescription = ""
        self.titleColor = 0xFF5733
        self.author = ""
        self.authorUrl = ""
        self.authorIconUrl = ""
        self.thumbnailUrl = ""
        self.fields = []  # {name:"",value="",inline=False}
        self.footer = ""

    def setTitle(self, titleName, titleUrl, titleDescript, titleColor):
        self.title = titleName
        self.titleUrl = titleUrl
        self.titleDescription = titleDescript
        self.titleColor = titleColor
