import matplotlib.pyplot as plt
import numpy as np
from google.colab.patches import cv2_imshow
from google.colab import output
from IPython.display import display, Javascript, clear_output

def imMouseCallback(imgs, onmouse=None):
  if onmouse:
    js_code = Javascript('''
      var dragging = false;
      function callback(e, event_name){
          var x = e.offsetX;
          var y = e.offsetY;
          var event=0
          var flag=0;

          if(event_name =='mousedown'){
            if(e.button==0){
              event=1;

              dragging=true;
            }else if(e.button==2){
              event=2;
              flag+=2
            }
          }else if(event_name=='mouseup'){
            if(e.button==0){
              event=4;

              if(dragging) dragging=false;
            }else if(e.button==2){
              event=5;

            }
          }else if(event_name=='mousemove'){
            event=0;
            if(dragging){
              flag+=1
            }
            console.log(e.button)
          }

          if(e.altKey){
            flag+=32;
          }
          if(e.ctrlKey){
            flag+=8;
          }
          if(e.shiftKey){
            flag+=16
          }
          google.colab.kernel.invokeFunction('notebook.onmouse', [event, x, y, flag, null], {});
      }
      window.setTimeout(()=>{
        var img = document.querySelector('#output-area img');
        img.draggable=false;
        img.addEventListener('mousedown',(e)=>{
          callback(e, 'mousedown')
        });
        img.addEventListener('contextmenu', (e)=>{e.preventDefault();})
        img.addEventListener('mouseup', (e)=>{
          callback(e, 'mouseup')
        });
        img.addEventListener('mousemove',(e)=>{
          console.log('move')
          callback(e, 'mousemove')
        });
      }, 0);
    ''')
    cv2_imshow(imgs)
    output.register_callback('notebook.onmouse', onmouse)
    display(js_code)
  else:
    print('no mouse event!!')

