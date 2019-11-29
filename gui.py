##############################################################################
#                                  gui.py                                    #
##############################################################################


import cv2

win_name = "Imaging Workbench"

##############################################################################
# Print location of mouse click for user star select
def mouse_cb(event, y, x, flags, userData):
    # if event == cv2.EVENT_LBUTTONDOWN:
    #     print(f"({x}, {y})")
    if event == cv2.EVENT_LBUTTONDBLCLK:
        exit()

##############################################################################
def setup():
    win = cv2.namedWindow(win_name, flags=cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(win_name, mouse_cb)
    return win

# future tKinter GUI application
# root = tk.Tk()
# img = tk.PhotoImage(file="test.png")
# panel = tk.Label(root, image=img)
# panel.pack(side="bottom", fill="both", expand="yes")
# root.mainloop()s
