def version():
	return "GladUI v-0.2.2"

def features():
	features = '''
=========================    
GladUI v-0.2.2
=========================
What's NEW? :
 1) Added a new object as version to check the version of GladUI.
 2) New App(developer=True), for having developer options, so that if any problem is on the code of this library, it will be informed to you.\n    You can change it any time!.
 
'''
	return features

def Documentation():
    text = '''
=========================
GladUI v-0.2.2 - Documentation
=========================

GladUI is a high-level GUI (Graphical User Interface) framework included in the Gladify package.  
It simplifies GUI development by providing an easy-to-use API for building applications.

Installation:
--------------
GladUI is part of Gladify. Install it using:

    pip install gladify

Importing the Library:
----------------------

You can import the library in two ways:

METHOD 1:
  
    from gladify.GladUI import App, Tools

    app = App()
    tools = Tools(app)  # Pass 'app' to Tools to connect it to the main window

METHOD 2:
  
    import gladify.GladUI as GladUI  # This imports the GladUI library from gladify

    app = GladUI.App()
    tools = GladUI.Tools(app)

Explanation:
- `App()` helps you create your app's root window, set the title, size, and more.
- `Tools(app)` allows you to add UI components like `Label`, `Button`, etc., and manage layouts.

--------------------------------------
1) Creating a Basic Application Window
--------------------------------------

Use the `App` class to create a basic application window.

Example:

    from gladify.GladUI import App

    app = App(name="My First GladUI App")
    app.run()

Explanation:
- The `App` class initializes a GUI window with a given title.
- The `run()` function starts the GUI event loop and displays the window.

--------------------------------------
2) Setting Developer Mode (Debugging)
--------------------------------------

Developer mode allows error messages to be displayed in the console.

Example:

    app = App(name="Debug Mode", developer=True)
    app.run()

--------------------------------------
3) Changing the Application Icon
--------------------------------------

You can set a custom icon for the application using the `icon` parameter.

Example:

    app = App(name="Icon Example", icon="path/to/icon.png")
    app.run()

--------------------------------------
4) Setting Window Resolution
--------------------------------------

The `resolution` parameter defines the width and height of the application window.

Example:

    app = App(name="Sized App", resolution="400x300")
    app.run()

--------------------------------------
5) Changing Theme
--------------------------------------

The `theme` parameter allows changing the theme of your app.

Example:

    app = App(name="Colored App", theme="light")
    app.run()
    
Note: The default theme is 'dark'. Available options: 'dark', 'light'.

--------------------------------------
6) Packing and Placing Widgets
--------------------------------------

All Tkinter functions like `.config()`, `.pack()`, `.place()` can be used.  
To simplify layout management, use `tools.pack()`, `tools.place()`, and `tools.grid()`.

Example:

    from gladify.GladUI import App, Tools

    app = App()
    tools = Tools(app)

    label = tools.Label("Hello, World!")
    tools.pack(label, center=True)

    app.run()

--------------------------------------
7) Running the Application
--------------------------------------

The `run()` function must be called to start the app.

Example:

    app = App()
    app.run()

--------------------------------------
8) Using UI Components
--------------------------------------

GladUI provides built-in components for UI design.

Example:

    button = tools.Button("Click Me", on_pressed=lambda: print("Button Clicked"))
    tools.pack(button, center=True)

    label = tools.Label("This is a Label")
    tools.pack(label)

    entry = tools.LineEdit(placeholder="Enter text here")
    tools.pack(entry)

    app.run()

--------------------------------------
9) More UI Components
--------------------------------------

- `tools.ComboBox(values=["Option1", "Option2"])` ? Dropdown menu.
- `tools.ListBox(items=["Item1", "Item2"])` ? Listbox.
- `tools.CheckButton("Check Me")` ? Checkbox.
- `tools.RadioButton("Option1", value=1, variable=var)` ? Radio button.
- `tools.ProgressBar(max_value=100, mode="determinate")` ? Progress bar.
- `tools.Slider(from_=0, to=100)` ? Slider.
- `tools.FileDialog(mode="open")` ? Open file dialog.

--------------------------------------
10) MessageBox
--------------------------------------

Show a message box with a title, text, and an OK button.

Example:

    tools.MessageBox(title="Info", text="This is a message!")

--------------------------------------
11) Scheduling Functions
--------------------------------------

Use `tools.schedule()` to run a function after a delay.

Example:

    def say_hello():
        print("Hello after 3 seconds!")

    tools.schedule(3, say_hello)

--------------------------------------
12) Getting Data from Inputs
--------------------------------------

Example:

    entry = tools.LineEdit(placeholder="Enter Name")
    tools.pack(entry)

    def show_data():
        print("Input:", tools.getData(entry))

    button = tools.Button("Submit", on_pressed=show_data)
    tools.pack(button)

    app.run()

--------------------------------------
13) Creating a Menu Bar
--------------------------------------

You can create a menu bar using `tools.MenuBar()`.

Example:

    menu = tools.MenuBar(["File", "Edit", "Help"])
    tools.pack(menu, fill=True)

--------------------------------------
14) Customizing Fonts
--------------------------------------

You can change font styles for UI components.

Example:

    label = tools.Label("Styled Text", font=("Arial", 16, "bold"))
    tools.pack(label)

--------------------------------------
15) Changing Background Color
--------------------------------------

Use `bg_color` to change background color.

Example:

    app = App(bg_color="lightblue")
    app.run()

--------------------------------------
16) Handling Key Press Events
--------------------------------------

Example:

    def key_pressed(event):
        print(f"Key Pressed: {event.keysym}")

    app.window.bind("<KeyPress>", key_pressed)
    app.run()

--------------------------------------
17) Handling Mouse Events
--------------------------------------

Example:

    def on_click(event):
        print(f"Mouse clicked at ({event.x}, {event.y})")

    app.window.bind("<Button-1>", on_click)
    app.run()

--------------------------------------
18) Creating a Canvas
--------------------------------------

You can draw shapes using `Canvas`.

Example:

    canvas = tools.Canvas(width=300, height=200, bg="white")
    tools.pack(canvas)

--------------------------------------
19) Creating a Frame
--------------------------------------

Use `Frame` to group multiple widgets.

Example:

    frame = tools.Frame()
    tools.pack(frame)

--------------------------------------
20) Creating a Scrollable Text Box
--------------------------------------

Example:

    text_box = tools.TextBox(height=5, width=40, scroll=True)
    tools.pack(text_box)

--------------------------------------
21) Creating a Status Bar
--------------------------------------

Example:

    status = tools.Label("Status: Ready")
    tools.pack(status, side="bottom", fill=True)

--------------------------------------
22) Creating a Custom Dialog
--------------------------------------

Example:

    def custom_dialog():
        tools.MessageBox(title="Alert", text="This is a custom dialog!")

    button = tools.Button("Show Dialog", on_pressed=custom_dialog)
    tools.pack(button)

--------------------------------------
23) Closing the Application
--------------------------------------

To close the application:

    tools.quit()

--------------------------------------
24) Handling Errors
--------------------------------------

If an error occurs, check if:
- The correct parameter types are used.
- The functions are called properly.

=========================
End of Documentation
=========================
'''
    return text
