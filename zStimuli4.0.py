
########################################################################################################################################################################
# Codes start

# 获取所有要用到的包
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import serial
from tkinter.font import Font
from tkinter import scrolledtext
import os
import configparser
from tkinter import *
import subprocess
from tkinter import filedialog


# 定义全局变量
timer_running = False
timer_time = 0
power_timer_running = False
power_timer_time = 0

# 逐个检查有无COM串口可用，选择可用的串口打开程序，没有可用的串口也打开
try:
    ports = list(serial.tools.list_ports.comports())
    if len(ports) > 0:
        ser = serial.Serial(ports[0].device, 9600, 8)
    else:
        ser = None
except:
    ser = None

#记录程序打开次数于.int文件
config = configparser.ConfigParser()
config.read('config.ini')
if not config.has_section('Count'):
    config.add_section('Count')
    config.set('Count', 'count', '0')
count = int(config.get('Count', 'count'))
count += 1
config.set('Count', 'count', str(count))
with open('config.ini', 'w') as f:
    config.write(f)
def show_count():
    messagebox.showinfo("Count", f"Program opened {count} times")


## 定义所有函数
def on_slider_change(value):
    pin = pin_entry.get()
    ser.write(f"{pin},{value}\n".encode())



def led_on():
    pin = pin_entry.get()
    global power_timer_running, power_timer_time
    power_timer_running = True
    power_timer_time = 0
    ser.write(f'H{pin}'.encode())
    
def led_off():
    pin = pin_entry.get()
    global power_timer_running
    power_timer_running = False
    ser.write(f'L{pin}'.encode())
    power_timer_listbox.itemconfig(0, {"fg": "red"})

def blink():
    if ser is not None:
        global timer_running, timer_time
        timer_running = True
        timer_time = 0
        on_time = on_entry.get().split()[0]
        off_time = off_entry.get().split()[0]
        pin = pin_entry.get()
        ser.write(f'B{pin} {on_time} {off_time}'.encode())

def stop_blink():
    global timer_running
    timer_running = False
    ser.write(b'S')
    timer_listbox.itemconfig(0, {"fg": "red"})

def close_serial():
    if ser is not None and ser.is_open:
        ser.close()
        messagebox.showinfo("Success", f"Serial port closed successfully")

def open_serial():
    global ser
    if 'ser' not in globals():
        com = com_entry.get()
        ser = serial.Serial(com, 9600)
    if not ser.is_open:
        com = com_entry.get()
        ser.port = com
        print(f"Trying to open serial port {com}")
        ser.open()
        if ser.is_open:
            print(f"Serial port {com} opened successfully")
        else:
            print(f"Failed to open serial port {com}")

def about():
    messagebox.showinfo("About", "zStimuli: Version 4.0.0\n\nOn Python\nWith ChatGPT\nDevelopmented by WANG KUI @ION\nContact: kwang@gmx.com")

def update_timer():
    global timer_time
    if timer_running:
        timer_time += 1
        timer_listbox.delete(0)
        timer_listbox.insert(0, f"Time: {format_time(timer_time)}")
        timer_listbox.itemconfig(0, {"fg": "black"})
    else:
        timer_listbox.itemconfig(0, {"fg": "grey"})
    root.after(1000, update_timer)

def format_time(seconds): # 把时间转化为HH:MM:SS格式
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def update_power_timer():
    global power_timer_time
    if power_timer_running:
        power_timer_time += 1
        power_timer_listbox.delete(0)
        power_timer_listbox.insert(0, f"Time: {format_time(power_timer_time)}")
        power_timer_listbox.itemconfig(0, {"fg": "black"})
    else:
        power_timer_listbox.itemconfig(0, {"fg": "grey"})
    root.after(1000, update_power_timer)

def on_key(event):
    event.widget.config(foreground="black")

def countdown(count):
    if count > 0:
        messagebox.showinfo("Exiting", f"Exiting in {count} seconds...")
        root.after(1000, countdown, count-1)
    else:
        root.quit()

def on_closing():
    if messagebox.askyesno("Exit", "确认已经断开串口通信？\n\nConfirm serial disconnection?"):
        root.destroy()

def open_serial():
    if not ser.is_open:
        com = com_entry.get()
        ser.port = com
        ser.open()
        if ser.is_open:
            messagebox.showinfo("Success", f"Serial port {com} opened successfully")

def show_error():
    messagebox.showerror("Let me help you~", "请用重新用Arduino IDE向单片机烧录代码！\n\n瓜基本保熟~\n\nPlease update the code in File menu again using the Arduino IDE!")

def update_arduino(): #在运行程序时，如果出现错误，将弹出一个消息框显示错误消息。
    try:
        # Your code here
        print("Hello, World!")
        # Add more code here if needed
    except Exception as e:
        messagebox.showerror("Error", str(e))



def show_arduino_code():
    code_window = tk.Toplevel(root)
    code_window.title("Arduino Code")
    text = tk.Text(code_window)
    text.pack()
    arduino_code = """
//Update this code onto your Arduino before use~
//Use Arduino IDE!

////////////////////////////////////////////////////////////////////////
// Start

int ledPin = 13;
int onTime = 100;
int offTime = 100;
bool blinking = false;

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'H') {
      ledPin = Serial.parseInt();
      pinMode(ledPin, OUTPUT);
      digitalWrite(ledPin, HIGH);
    } else if (cmd == 'L') {
      ledPin = Serial.parseInt();
      pinMode(ledPin, OUTPUT);
      digitalWrite(ledPin, LOW);
    } else if (cmd == 'B') {
      ledPin = Serial.parseInt();
      pinMode(ledPin, OUTPUT);
      onTime = Serial.parseInt();
      offTime = Serial.parseInt();
      blinking = true;
    } else if (cmd == 'S') {
      blinking = false;
    }
  }
  if (blinking) {
    digitalWrite(ledPin, HIGH);
    delay(onTime);
    digitalWrite(ledPin, LOW);
    delay(offTime);
  }
}

// End
////////////////////////////////////////////////////////////////////////
"""
    text.insert(tk.END, arduino_code)

    def copy_all(): # 子函数
        code_window.clipboard_clear()
        code_window.clipboard_append(text.get("1.0", tk.END))
        copy_button.config(text="Copied")

    def save_all():
        # 创建 temp 文件夹（如果不存在）
        os.makedirs('temp', exist_ok=True)
        # 指定文件的完整路径
        file_path = os.path.join('temp', 'temp.ino')
        with open(file_path, "w") as f:
            f.write(text.get("1.0", tk.END))
    
    def upload_all():
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename()
        # arduino-cli 工具的路径
        arduino_cli_path = 'C:\\ProgramData\\arduino-cli\\arduino-cli.exe'
        # 定义 fqbn 和 port
        fqbn = 'arduino:avr:uno'
        port = com_entry.get()
          # 获取项目文件夹的路径
        project_dir = os.path.dirname(file_path)
        # 编译项目
        compile_cmd = [arduino_cli_path, 'compile', '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(e.output.decode('gbk'))
            messagebox.showerror("Error", f"Compilation failed! Error: {e.output.decode()}")
            return
        # 使用 arduino-cli 工具上传文件
        project_dir = os.path.dirname(file_path)
        cmd = [arduino_cli_path, 'upload', '-p', port, '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            messagebox.showinfo("Success", "Upload successful!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Upload failed! Error: {e.output.decode('gbk', errors='ignore')}")

    copy_button = ttk.Button(code_window, text="Copy all code", command=copy_all)
    copy_button.pack()

    save_button = ttk.Button(code_window, text="Save code as .ino", command=save_all)
    save_button.pack()

    upload_button = ttk.Button(code_window, text="Upload to Arduino UNO", command=upload_all)
    upload_button.pack()








def show_voltage_code():
    code_window = tk.Toplevel(root)
    code_window.title("Arduino Code")
    text = tk.Text(code_window)
    text.pack()
    arduino_code = """
//Update this code onto your Arduino before use~
//Use Arduino IDE!

////////////////////////////////////////////////////////////////////////
// Start

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    int pin = Serial.parseInt();
    int value = Serial.parseInt();
    pinMode(pin, OUTPUT);
    analogWrite(pin, value);
  }
}

// End
////////////////////////////////////////////////////////////////////////
"""
    text.insert(tk.END, arduino_code)

    def copy_all(): # 子函数
        code_window.clipboard_clear()
        code_window.clipboard_append(text.get("1.0", tk.END))
        copy_button.config(text="Copied")

    def save_all():
        # 创建 temp 文件夹（如果不存在）
        os.makedirs('temp', exist_ok=True)
        # 指定文件的完整路径
        file_path = os.path.join('temp', 'temp.ino')
        with open(file_path, "w") as f:
            f.write(text.get("1.0", tk.END))
        # 弹出对话框提醒用户
        messagebox.showinfo("Success", "File saved successfully!")
    
    def upload_all():
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename()
        # arduino-cli 工具的路径
        arduino_cli_path = 'C:\\ProgramData\\arduino-cli\\arduino-cli.exe'
        # 定义 fqbn 和 port
        fqbn = 'arduino:avr:uno'
        port = com_entry.get()
          # 获取项目文件夹的路径
        project_dir = os.path.dirname(file_path)
        # 编译项目
        compile_cmd = [arduino_cli_path, 'compile', '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(e.output.decode('gbk'))
            messagebox.showerror("Error", f"Compilation failed! Error: {e.output.decode()}")
            return
        # 使用 arduino-cli 工具上传文件
        project_dir = os.path.dirname(file_path)
        cmd = [arduino_cli_path, 'upload', '-p', port, '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            messagebox.showinfo("Success", "Upload successful!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Upload failed! Error: {e.output.decode('gbk', errors='ignore')}")

    copy_button = ttk.Button(code_window, text="Copy all code", command=copy_all)
    copy_button.pack()

    save_button = ttk.Button(code_window, text="Save code as .ino", command=save_all)
    save_button.pack()

    upload_button = ttk.Button(code_window, text="Upload to Arduino UNO", command=upload_all)
    upload_button.pack()


def show_bluetooth_code():
    code_window = tk.Toplevel(root)
    code_window.title("蓝牙刺激器代码")
    text = tk.Text(code_window)
    text.pack()
    arduino_code = """
//Update this code onto your Arduino before use~
//Use Arduino IDE!

////////////////////////////////////////////////////////////////////////
// Start

#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX

void setup() {
  mySerial.begin(9600);
}

void loop() {
  if (mySerial.available()) {
    String input = mySerial.readStringUntil(';');
    input.trim();
    mySerial.println(input);
    char command = input.charAt(2);
    int pin = input.substring(0, 2).toInt();
    pinMode(pin, OUTPUT);
    if (command == 'o') {
      digitalWrite(pin, HIGH);
    } else if (command == 'x') {
      digitalWrite(pin, LOW);
    } else if (command == 'b') {
      int brightness = input.substring(4).toInt();
      analogWrite(pin, map(brightness, 0, 100, 0, 255));
    } else if (command == 'k') {
      int index1 = input.indexOf(' ', 4);
      int index2 = input.indexOf(' ', index1 + 1);
      int onTime = input.substring(4, index1).toInt();
      int offTime = input.substring(index1 + 1, index2).toInt();
      int duration = input.substring(index2 + 1).toInt();
      unsigned long startTime = millis();
      while (millis() - startTime < duration) {
        digitalWrite(pin, HIGH);
        delay(onTime);
        digitalWrite(pin, LOW);
        delay(offTime);
      }
    }
  }
}

// End
////////////////////////////////////////////////////////////////////////
"""
    text.insert(tk.END, arduino_code)

    def copy_all(): # 子函数
        code_window.clipboard_clear()
        code_window.clipboard_append(text.get("1.0", tk.END))
        copy_button.config(text="Copied")

    def save_all():
        # 创建 temp 文件夹（如果不存在）
        os.makedirs('temp', exist_ok=True)
        # 指定文件的完整路径
        file_path = os.path.join('temp', 'temp.ino')
        with open(file_path, "w") as f:
            f.write(text.get("1.0", tk.END))
        # 弹出对话框提醒用户
        messagebox.showinfo("Success", "File saved successfully!")
    
    def upload_all():
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename()
        # arduino-cli 工具的路径
        arduino_cli_path = 'C:\\ProgramData\\arduino-cli\\arduino-cli.exe'
        # 定义 fqbn 和 port
        fqbn = 'arduino:avr:uno'
        port = com_entry.get()
          # 获取项目文件夹的路径
        project_dir = os.path.dirname(file_path)
        # 编译项目
        compile_cmd = [arduino_cli_path, 'compile', '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(e.output.decode('gbk'))
            messagebox.showerror("Error", f"Compilation failed! Error: {e.output.decode()}")
            return
        # 使用 arduino-cli 工具上传文件
        project_dir = os.path.dirname(file_path)
        cmd = [arduino_cli_path, 'upload', '-p', port, '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            messagebox.showinfo("Success", "Upload successful!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Upload failed! Error: {e.output.decode('gbk', errors='ignore')}")

    copy_button = ttk.Button(code_window, text="Copy all code", command=copy_all)
    copy_button.pack()

    save_button = ttk.Button(code_window, text="Save code as .ino", command=save_all)
    save_button.pack()

    upload_button = ttk.Button(code_window, text="Upload to Arduino UNO", command=upload_all)
    upload_button.pack()

def show_pitches_code():
    code_window = tk.Toplevel(root)
    code_window.title("音调文件")
    text = tk.Text(code_window)
    text.pack()
    arduino_code = """
//存在Arduino.ino同目录下的pitches.h中
//

////////////////////////////////////////////////////////////////////////
// Start

/*************************************************
 * Public Constants
 *************************************************/

#define NOTE_B0  31
#define NOTE_C1  33
#define NOTE_CS1 35
#define NOTE_D1  37
#define NOTE_DS1 39
#define NOTE_E1  41
#define NOTE_F1  44
#define NOTE_FS1 46
#define NOTE_G1  49
#define NOTE_GS1 52
#define NOTE_A1  55
#define NOTE_AS1 58
#define NOTE_B1  62
#define NOTE_C2  65
#define NOTE_CS2 69
#define NOTE_D2  73
#define NOTE_DS2 78
#define NOTE_E2  82
#define NOTE_F2  87
#define NOTE_FS2 93
#define NOTE_G2  98
#define NOTE_GS2 104
#define NOTE_A2  110
#define NOTE_AS2 117
#define NOTE_B2  123
#define NOTE_C3  131
#define NOTE_CS3 139
#define NOTE_D3  147
#define NOTE_DS3 156
#define NOTE_E3  165
#define NOTE_F3  175
#define NOTE_FS3 185
#define NOTE_G3  196
#define NOTE_GS3 208
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_CS4 277
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_FS4 370
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_CS5 554
#define NOTE_D5  587
#define NOTE_DS5 622
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_FS5 740
#define NOTE_G5  784
#define NOTE_GS5 831
#define NOTE_A5  880
#define NOTE_AS5 932
#define NOTE_B5  988
#define NOTE_C6  1047
#define NOTE_CS6 1109
#define NOTE_D6  1175
#define NOTE_DS6 1245
#define NOTE_E6  1319
#define NOTE_F6  1397
#define NOTE_FS6 1480
#define NOTE_G6  1568
#define NOTE_GS6 1661
#define NOTE_A6  1760
#define NOTE_AS6 1865
#define NOTE_B6  1976
#define NOTE_C7  2093
#define NOTE_CS7 2217
#define NOTE_D7  2349
#define NOTE_DS7 2489
#define NOTE_E7  2637
#define NOTE_F7  2794
#define NOTE_FS7 2960
#define NOTE_G7  3136
#define NOTE_GS7 3322
#define NOTE_A7  3520
#define NOTE_AS7 3729
#define NOTE_B7  3951
#define NOTE_C8  4186
#define NOTE_CS8 4435
#define NOTE_D8  4699
#define NOTE_DS8 4978
 

// End
////////////////////////////////////////////////////////////////////////
"""
    text.insert(tk.END, arduino_code)

    def copy_all(): # 子函数
        code_window.clipboard_clear()
        code_window.clipboard_append(arduino_code)
        copy_button.config(text="Copied")

    copy_button = ttk.Button(code_window, text="Copy all code", command=copy_all)
    copy_button.pack()

def show_tiger_code():
    code_window = tk.Toplevel(root)
    code_window.title("两只老虎")
    text = tk.Text(code_window)
    text.pack()
    arduino_code = """
//Update this code onto your Arduino before use~
//Use Arduino IDE!

////////////////////////////////////////////////////////////////////////
// Start

#include "pitches.h"
int buzzer = 8; // 定义蜂鸣器连接的针脚
int melody[] = { // 定义旋律
  NOTE_C4, NOTE_D4, NOTE_E4, NOTE_C4,
  NOTE_C4, NOTE_D4, NOTE_E4, NOTE_C4,
  NOTE_E4, NOTE_F4, NOTE_G4,
  NOTE_E4, NOTE_F4, NOTE_G4,
  NOTE_G4, NOTE_A4, NOTE_G4, NOTE_F4, NOTE_E4, NOTE_C4,
  NOTE_G4, NOTE_A4, NOTE_G4, NOTE_F4, NOTE_E4, NOTE_C4,
  NOTE_C4, NOTE_G3, NOTE_C4,
  NOTE_C4, NOTE_G3, NOTE_C4
};
int noteDurations[] = { // 定义每个音符的持续时间
  8, 8, 8, 8,
  8, 8, 8, 8,
  8, 8, 2,
  8, 8, 2,
  8, 16,16 ,16 ,16 ,2 ,
  8 ,16 ,16 ,16 ,16 ,2 ,
  8 ,8 ,2 ,
  8 ,8 ,2 
};

void setup() {
}

void loop() {
    for (int thisNote = 0; thisNote < sizeof(melody) / sizeof(int); thisNote++) { // 遍历旋律中的每个音符
        int noteDuration = 1000 / noteDurations[thisNote]; // 计算音符持续时间
        tone(buzzer,melody[thisNote],noteDuration); // 播放音符
        int pauseBetweenNotes = noteDuration *1.30; // 计算两个音符之间的暂停时间
        delay(pauseBetweenNotes); // 暂停
        noTone(buzzer); // 停止播放音符
    }
}

// End
////////////////////////////////////////////////////////////////////////
"""
    text.insert(tk.END, arduino_code)

    def copy_all(): # 子函数
        code_window.clipboard_clear()
        code_window.clipboard_append(text.get("1.0", tk.END))
        copy_button.config(text="Copied")

    def save_all():
        # 创建 temp 文件夹（如果不存在）
        os.makedirs('temp', exist_ok=True)
        # 指定文件的完整路径
        file_path = os.path.join('temp', 'temp.ino')
        with open(file_path, "w") as f:
            f.write(text.get("1.0", tk.END))
        # 弹出对话框提醒用户
        messagebox.showinfo("Success", "File saved successfully!")
    
    def upload_all():
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename()
        # arduino-cli 工具的路径
        arduino_cli_path = 'C:\\ProgramData\\arduino-cli\\arduino-cli.exe'
        # 定义 fqbn 和 port
        fqbn = 'arduino:avr:uno'
        port = com_entry.get()
          # 获取项目文件夹的路径
        project_dir = os.path.dirname(file_path)
        # 编译项目
        compile_cmd = [arduino_cli_path, 'compile', '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(e.output.decode('gbk'))
            messagebox.showerror("Error", f"Compilation failed! Error: {e.output.decode()}")
            return
        # 使用 arduino-cli 工具上传文件
        project_dir = os.path.dirname(file_path)
        cmd = [arduino_cli_path, 'upload', '-p', port, '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            messagebox.showinfo("Success", "Upload successful!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Upload failed! Error: {e.output.decode('gbk', errors='ignore')}")

    copy_button = ttk.Button(code_window, text="Copy all code", command=copy_all)
    copy_button.pack()

    save_button = ttk.Button(code_window, text="Save code as .ino", command=save_all)
    save_button.pack()

    upload_button = ttk.Button(code_window, text="Upload to Arduino UNO", command=upload_all)
    upload_button.pack()

def show_birthday_code():
    code_window = tk.Toplevel(root)
    code_window.title("生日歌")
    text = tk.Text(code_window)
    text.pack()
    arduino_code = """
//Update this code onto your Arduino before use~
//Use Arduino IDE!

////////////////////////////////////////////////////////////////////////
// Start

#include "pitches.h"
int buzzer = 8; // 定义蜂鸣器连接的针脚
int melody[] = { // 定义旋律
  NOTE_C4, NOTE_C4, NOTE_D4, NOTE_C4, NOTE_F4, NOTE_E4,
  NOTE_C4, NOTE_C4, NOTE_D4, NOTE_C4, NOTE_G4, NOTE_F4,
  NOTE_C4, NOTE_C4, NOTE_C5, NOTE_A4, NOTE_F4, NOTE_E4, NOTE_D4,
  NOTE_AS4,NOTE_AS4,NOTE_A4,NOTE_F4,NOTE_G4,NOTE_F4
};
int noteDurations[] = { // 定义每个音符的持续时间
  8 ,8 ,8 ,8 ,8 ,2 ,
  8 ,8 ,8 ,8 ,8 ,2 ,
  8 ,8 ,8 ,8 ,8 ,8 ,2 ,
  8 ,8 ,8 ,8 ,8 ,2
};

void setup() {
}

void loop() {
    for (int thisNote = 0; thisNote < sizeof(melody) / sizeof(int); thisNote++) { // 遍历旋律中的每个音符
        int noteDuration = 1000 / noteDurations[thisNote]; // 计算音符持续时间
        tone(buzzer,melody[thisNote],noteDuration); // 播放音符
        int pauseBetweenNotes = noteDuration *1.30; // 计算两个音符之间的暂停时间
        delay(pauseBetweenNotes); // 暂停
        noTone(buzzer); // 停止播放音符
    }
}

// End
////////////////////////////////////////////////////////////////////////
"""
    text.insert(tk.END, arduino_code)

    def copy_all(): # 子函数
        code_window.clipboard_clear()
        code_window.clipboard_append(text.get("1.0", tk.END))
        copy_button.config(text="Copied")

    def save_all():
        # 创建 temp 文件夹（如果不存在）
        os.makedirs('temp', exist_ok=True)
        # 指定文件的完整路径
        file_path = os.path.join('temp', 'temp.ino')
        with open(file_path, "w") as f:
            f.write(text.get("1.0", tk.END))
        # 弹出对话框提醒用户
        messagebox.showinfo("Success", "File saved successfully!")
    
    def upload_all():
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename()
        # arduino-cli 工具的路径
        arduino_cli_path = 'C:\\ProgramData\\arduino-cli\\arduino-cli.exe'
        # 定义 fqbn 和 port
        fqbn = 'arduino:avr:uno'
        port = com_entry.get()
          # 获取项目文件夹的路径
        project_dir = os.path.dirname(file_path)
        # 编译项目
        compile_cmd = [arduino_cli_path, 'compile', '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(e.output.decode('gbk'))
            messagebox.showerror("Error", f"Compilation failed! Error: {e.output.decode()}")
            return
        # 使用 arduino-cli 工具上传文件
        project_dir = os.path.dirname(file_path)
        cmd = [arduino_cli_path, 'upload', '-p', port, '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            messagebox.showinfo("Success", "Upload successful!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Upload failed! Error: {e.output.decode('gbk', errors='ignore')}")

    copy_button = ttk.Button(code_window, text="Copy all code", command=copy_all)
    copy_button.pack()

    save_button = ttk.Button(code_window, text="Save code as .ino", command=save_all)
    save_button.pack()

    upload_button = ttk.Button(code_window, text="Upload to Arduino UNO", command=upload_all)
    upload_button.pack()

def show_cris_code():
    code_window = tk.Toplevel(root)
    code_window.title("圣诞歌")
    text = tk.Text(code_window)
    text.pack()
    arduino_code = """
//Update this code onto your Arduino before use~
//Use Arduino IDE!

嘿嘿，想屁吃。

// End
////////////////////////////////////////////////////////////////////////
"""
    text.insert(tk.END, arduino_code)

    def copy_all(): # 子函数
        code_window.clipboard_clear()
        code_window.clipboard_append(text.get("1.0", tk.END))
        copy_button.config(text="Copied")

    def save_all():
        # 创建 temp 文件夹（如果不存在）
        os.makedirs('temp', exist_ok=True)
        # 指定文件的完整路径
        file_path = os.path.join('temp', 'temp.ino')
        with open(file_path, "w") as f:
            f.write(text.get("1.0", tk.END))
    
    def upload_all():
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename()
        # arduino-cli 工具的路径
        arduino_cli_path = 'C:\\ProgramData\\arduino-cli\\arduino-cli.exe'
        # 定义 fqbn 和 port
        fqbn = 'arduino:avr:uno'
        port = com_entry.get()
          # 获取项目文件夹的路径
        project_dir = os.path.dirname(file_path)
        # 编译项目
        compile_cmd = [arduino_cli_path, 'compile', '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(e.output.decode('gbk'))
            messagebox.showerror("Error", f"Compilation failed! Error: {e.output.decode()}")
            return
        # 使用 arduino-cli 工具上传文件
        project_dir = os.path.dirname(file_path)
        cmd = [arduino_cli_path, 'upload', '-p', port, '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            messagebox.showinfo("Success", "Upload successful!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Upload failed! Error: {e.output.decode('gbk', errors='ignore')}")

    copy_button = ttk.Button(code_window, text="Copy all code", command=copy_all)
    copy_button.pack()

    save_button = ttk.Button(code_window, text="Save code as .ino", command=save_all)
    save_button.pack()

    upload_button = ttk.Button(code_window, text="Upload to Arduino UNO", command=upload_all)
    upload_button.pack()


def upload_codes():
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename()
        # arduino-cli 工具的路径
        arduino_cli_path = 'C:\\ProgramData\\arduino-cli\\arduino-cli.exe'
        # 定义 fqbn 和 port
        fqbn = 'arduino:avr:uno'
        port = com_entry.get()
          # 获取项目文件夹的路径
        project_dir = os.path.dirname(file_path)
        # 编译项目
        compile_cmd = [arduino_cli_path, 'compile', '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(e.output.decode('gbk'))
            messagebox.showerror("Error", f"Compilation failed! Error: {e.output.decode()}")
            return
        # 使用 arduino-cli 工具上传文件
        project_dir = os.path.dirname(file_path)
        cmd = [arduino_cli_path, 'upload', '-p', port, '--fqbn', fqbn, project_dir]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            messagebox.showinfo("Success", "Upload successful!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Upload failed! Error: {e.output.decode('gbk', errors='ignore')}")

### 构建可视化窗口

## 根窗口
root = tk.Tk()
root.title("zStimuli V4.0")

## 根菜单栏
menubar = tk.Menu(root)

# File 栏目
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Upload codes", command=upload_codes)





# Codes子菜单
codesmenu = tk.Menu(filemenu, tearoff=0)
codesmenu.add_command(label="Arduino Code for Mode1", command=show_voltage_code)
codesmenu.add_command(label="Arduino Code for Mode2", command=show_arduino_code)
codesmenu.add_command(label="微信小程序 蓝牙刺激发生器", command=show_bluetooth_code)

# Music子菜单
musicmenu = tk.Menu(codesmenu, tearoff=0)
musicmenu.add_command(label="音调文件", command=show_pitches_code)
musicmenu.add_command(label="两只老虎", command=show_tiger_code)
musicmenu.add_command(label="生日歌", command=show_birthday_code)
musicmenu.add_command(label="圣诞歌", command=show_cris_code)
codesmenu.add_cascade(label="Music", menu=musicmenu)

filemenu.add_cascade(label="Arduino codes", menu=codesmenu)

# Music子菜单
serialmenu = tk.Menu(filemenu, tearoff=0)
serialmenu.add_command(label="Open Serial", command=open_serial)
serialmenu.add_command(label="Close Serial", command=close_serial)
filemenu.add_cascade(label="Serial control", menu=serialmenu)
filemenu.add_separator()
filemenu.add_command(label="About", command=about)


menubar.add_cascade(label="File", menu=filemenu)

# Count 栏目
countmenu = tk.Menu(menubar, tearoff=0)
countmenu.add_command(label="Show Count", command=show_count)
countmenu.add_separator()
countmenu.add_command(label="About", command=about)
menubar.add_cascade(label="Count", menu=countmenu)

# Help菜单
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Why this does not work?", command=show_error)
helpmenu.add_separator()
helpmenu.add_command(label="About", command=about)
menubar.add_cascade(label="Help", menu=helpmenu)

## Modes菜单
def show_mode1():
    set_frame.grid()
    pin_frame.grid()
    power_frame.grid_remove()
    blink_frame.grid_remove()
def show_mode2():
    set_frame.grid_remove()
    cpp_frame.grid()
    blink_frame.grid()
    power_frame.grid()
def show_allmodes():
    set_frame.grid()
    cpp_frame.grid()
    blink_frame.grid()
    power_frame.grid()
modesmenu = tk.Menu(menubar, tearoff=0)

modesmenu.add_command(label="Mode1", command=show_mode1)
modesmenu.add_command(label="Mode2", command=show_mode2)
modesmenu.add_separator()
modesmenu.add_command(label="All modes", command=show_allmodes)
modesmenu.add_separator()
modesmenu.add_command(label="About", command=about)
menubar.add_cascade(label="Modes", menu=modesmenu)


# 终止菜单
root.config(menu=menubar)



## 顶级主窗口

top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0)



# Reset模块
set_frame = tk.Frame()
set_frame.grid(row=0, column=0)

# Restart模块
restart_frame = tk.LabelFrame(set_frame, text="RESET", labelanchor="n", foreground="deepskyblue",width=60, height=60)
restart_frame.grid(row=0, column=0)
restart_frame.grid_propagate(0)
def reset_serial():
    close_serial()
    root.after(1500, open_serial)
def on_click(event):
    canvas.itemconfig(circle, fill="grey")
    reset_serial()
    root.after(4000, lambda: canvas.itemconfig(circle, fill="magenta"))
canvas = tk.Canvas(restart_frame, width=30, height=30)
canvas.grid(row=0, column=0, sticky="ns")
circle = canvas.create_oval(5, 5, 25, 25, fill="magenta")
canvas.tag_bind(circle, "<Button-1>", on_click)

# Voltage模块
voltage_frame = tk.LabelFrame(set_frame, text="VOLTAGE", labelanchor="n", foreground="deepskyblue",width=80, height=215)
voltage_frame.grid(row=0, column=1)
voltage_frame.grid_propagate(0)
slider = Scale(voltage_frame, from_=0, to=255, orient=HORIZONTAL, command=on_slider_change, length=210)
slider.pack()



#Com Pin Power区域

cpp_frame = tk.Frame()
cpp_frame.grid(row=1, column=0)

# Com & Pin设置模块

pin_frame = tk.LabelFrame(cpp_frame, text="COM   &   PIN", labelanchor="n", foreground="deepskyblue")
pin_frame.grid(row=1, column=0)

com_entry = tk.Entry(pin_frame, width=8, justify='center')
com_entry.grid(row=1, column=0)
com_entry.insert(0, "COM5")
com_entry.config(foreground="grey")

pin_entry = tk.Entry(pin_frame, width=8, justify='center' )
pin_entry.grid(row=1, column=1)
pin_entry.insert(0, "6")
pin_entry.config(foreground="grey")
pin_entry.bind("<Key>", on_key)

com_button_on = ttk.Button(pin_frame, text="Serial On", command=open_serial, width=8)
com_button_on.grid(row=2, column=0)

style = ttk.Style()
style.configure('my.TButton', background='#FFE4E1')
com_button_off = ttk.Button(pin_frame, text="Serial Off", command=close_serial, width=8,style='my.TButton')
com_button_off.grid(row=2, column=1)



# Power模块

power_frame = tk.LabelFrame(cpp_frame, text="POWER", labelanchor="n", foreground="deepskyblue")
power_frame.grid(row=1, column=1)

on_button = ttk.Button(power_frame, text="On", command=led_on, width=8)
on_button.grid(row=1, column=2)

off_button = ttk.Button(power_frame, text="Off", command=led_off, width=8)
off_button.grid(row=1, column=3)

power_timer_listbox = tk.Listbox(power_frame, height=1, width=12)
power_timer_listbox.grid(row=0, column=0, columnspan=4)
power_timer_listbox.insert(0, "Time: 00:00:00")
power_timer_listbox.itemconfig(0, {"fg": "grey"})



# Blinking模块

blink_frame = tk.LabelFrame(root, text="BLINKING", labelanchor="n", foreground="deepskyblue")
blink_frame.grid(row=2, column=0)
# 时间设定区域
blk_time_frame = tk.Frame(blink_frame)
blk_time_frame.grid(row=0, column=0)

on_label = ttk.Label(blk_time_frame, text="On Delay")
on_label.grid(row=0, column=0)
on_entry = tk.Entry(blk_time_frame, width=10)
on_entry.grid(row=0, column=1)
on_entry.insert(0, "100 ms")
on_entry.config(foreground="grey")
on_entry.bind("<Key>", on_key)

off_label = ttk.Label(blk_time_frame, text="Off Delay")
off_label.grid(row=1, column=0)
off_entry = tk.Entry(blk_time_frame, width=10)
off_entry.grid(row=1, column=1)
off_entry.insert(0, "100 ms")
off_entry.config(foreground="grey")
off_entry.bind("<Key>", on_key)

# 时间显示和闪烁开关控制区域

blk_timer_frame = tk.Frame(blink_frame)
blk_timer_frame.grid(row=0, column=1)

timer_listbox = tk.Listbox(blk_timer_frame , height=1, width=12)
timer_listbox.grid(row=0, column=0, columnspan=4)
timer_listbox.insert(0, "Time: 00:00:00")
timer_listbox.itemconfig(0, {"fg": "grey"})

blink_button = ttk.Button(blk_timer_frame , text="Blink", command=blink,width=8)
blink_button.grid(row=1, column=2, rowspan=2)
stop_button = ttk.Button(blk_timer_frame , text="Stop", command=stop_blink,width=8)
stop_button.grid(row=1, column=3, rowspan=2)

## 循环
update_timer()
update_power_timer()
root.protocol("WM_DELETE_WINDOW", on_closing)

### 主循环
root.mainloop()



# Codes end
########################################################################################################################################################################
