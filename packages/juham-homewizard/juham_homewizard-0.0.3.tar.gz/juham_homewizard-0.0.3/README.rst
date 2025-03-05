Homewizard watermeter plugin for Juham™
=======================================

Description
-----------

Homewizard watermeter support for Juham™. Reads the watermeter with the specified
frequency (the default is 60s) and publishes the readings to Juham MQTT network.


.. image:: _static/images/homewizard_watermeter.png
   :alt: HomeWizard watermeter 
   :width: 640px
   :align: center  



Getting Started
---------------

### Installation

1. Install 

   .. code-block:: bash

      pip install juham-homewizard


      
2. Configure

To configure edit the `HomewizardWaterMeter*.json` configuration file to match your network and
desired reading frequency in seconds.

   .. code-block:: python

      {
        "url": "http://192.168.86.70/api/v1/data",
	"update_interval": 60
      }

