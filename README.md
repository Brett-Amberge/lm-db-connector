# LM Database Connector Omniverse Kit Extension

This project's purpose is to connect library parts and meshes stored in USD format to a SQL database that stores detailed and relevant information about each part. This allows for the maintance of a highly detailed, portable, and accurate digital twin for use in modeling and integration testing of various scenarios.

# Enabling this extension in Kit

This application works in any Omniverse Kit application the has an active Viewport window. To enable it, 

1. Clone this repository to a desired place on your machine with
> git clone https://github.com/Brett-Amberge/lm-db-connector.git
2. In the *Omniverse App* open extension manager: *Window* &rarr; *Extensions*.
3. In the *Extension Manager Window* open a settings page, with a small gear button in the top left bar.
4. Click the green + icon to add an additional path
5. In the settings page there is a list of *Extension Search Paths*. Add cloned repo `exts` subfolder there as another search path, i.e.: `C:\projects\kit-extension-template\exts`

![The Omniverse Kit extension manager](assets/ext_window.PNG)

6. The extension will now appear in the extension manager window. Simply toggle it on to enable it.

# Using this extension

Once the extension is enabled, a UI window will appear prompting for user credentials to connect to the database. Input your login information to connect, then selected any object in the scene. This will query the database using data stored in its USD file to see if information on that object is stored, then will display any info retrieved from the query in the Database Info window.

