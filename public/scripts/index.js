var ParentBox = React.createClass({

  /**
   * Request from the server the list of pipelines
   */
  _loadCommentsFromServer: function() {
    
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      ifModified: true,
      cache: true,

      success: function(data,text,res) {
        
        if (res.status == "200") {
          // change DOM only if 200, ignoring 304
          this.setState({data: data});
        }

      }.bind(this),

      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)

    });
  },

  getInitialState: function() {
    return {data: []};
  },

  componentDidMount: function() {
    this._loadCommentsFromServer();
    setInterval(this._loadCommentsFromServer, this.props.pollInterval);
  },

  render: function() {
    return (
      <div className="concourse-radiator">
        <h1>Moo Builds</h1>
        <PipelineList data={this.state.data} />
      </div>
    );
  }
});

/**
 * The list of all the pipelines
 */
var PipelineList = React.createClass({

  render: function() {

    var commentNodes = this.props.data.map(function(pipeline) {
      return (
        <Pipeline key={pipeline.name} name={pipeline.name} url={pipeline.url} paused={pipeline.paused} jobs={pipeline.jobs} />
      );
    });

    return (
      <div key='container-list' className="pipeline-list">
        {commentNodes}
      </div>
    );

  }
});

/**
 * One Pipeline box
 */
var Pipeline = React.createClass({

  render: function() {

    var jobNodes;
    if (this.props.paused) {

      // the pipeline is paused, no stripes are displayed, the box is solid gray
      jobNodes = "";
    }
    else {

      // Generate vertical stripes, representing job statuses insite the current pipeline
      var width = 250 / this.props.jobs.length;
      jobNodes = this.props.jobs.map(function(job) {
        return (
          <div className={ 'pipeline-job ' + job.status } style={{width: width}} />
        );
      });
    }


    return (
      <a key={ 'link-' + this.props.name } href={this.props.url} className="pipeline-link" target="_blank">
        <div key={ 'pipeline-' + this.props.name } className={ 'pipeline' + (this.props.paused ? ' paused' : '') }>
          
          <h2 className="pipeline-name" >
            {this.props.name}
          </h2>

          {jobNodes}

        </div>
      </a>
    );
  }
});

ReactDOM.render(
  <ParentBox url="/api/v1/pipelines" pollInterval={4000} />,document.getElementById('content')
);