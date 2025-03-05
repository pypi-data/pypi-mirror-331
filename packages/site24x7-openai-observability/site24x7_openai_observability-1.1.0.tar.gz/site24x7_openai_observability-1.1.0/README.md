Site24x7 OpenAI Observability
=========================================

**Instructions to add Site24x7 OpenAI Observability**

* Install the site24x7-openai module using the following command:

        pip install site24x7-openai-observability --upgrade

> *Note: If you are using a virtual environment, activate it and run the above command to install the site24x7-openai-observability package into your virtual environment.*

* Configure the license key, sample factor, and capture openai text using environment variables.

       $ export SITE24X7_LICENSE_KEY=<your site24x7 license key>
       $ export SITE24X7_SAMPLING_FACTOR=<set sampling factor by default 10>
       $ export SITE24X7_CAPTURE_OPENAI_TEXT=<set value by default True>


* Add the below code to your application's start file to integrate the observability agent:
        
        import os
        os.environ["SITE24X7_LICENSE_KEY"] = "<license_key or device_key>"
        import site24x7_openai_observability



