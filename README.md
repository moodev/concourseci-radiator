# ConcourseCI Radiator

**Radiator** - is the simple page that shows pipeline job statuses in one place. It suits to be displayed on a TV screen to give an overview of your [ConcourseCI](http://concourse.ci) builds. The Radiator polls the Concourse every 4 seconds for an updates and shows the actual information.

![ConcourseCI Radiator](https://github.com/moodev/concourseci-radiator/blob/master/public/images/Selection_034.jpg)

or, this is how it looks like on the TV wall:

![ConcourseCI Radiator on TV wall](https://github.com/moodev/concourseci-radiator/blob/master/public/images/concourse-radiator-on-wall.jpg)

The back-end is the utterly simple proxy server written in Python (using [Flask framework](http://flask.pocoo.org)) and the front-end is made using the [ReactJS framework](http://reactjs.net).

To run this service, you need to install requirements for your Python:

```bash
pip install -r requirements.txt
```
edit the file **config.py** providing correct URL and credentials for your Concourse server and then you can start it something like that:

```bash
python proxy.py
```

Now you can navigate to your browser at http://localhost:3001 and you will see the Radiator for your ConcourseCI.

Enjoy!
