from enum import Enum

class Constants:

    NoCodingLanguageChosenException = "Coding Language Not Chosen"
    DotNetSupportException = ".NET Support is not enabled"
    PythonSupportException = "Python Support is not enabled"

    class InputType(Enum):
        CustomClass = "customclass"
    
    class CodingLanguage(Enum):
        DotNet = "dotnet"
        Python = "python"