var ParentBox = React.createClass({

  /**
   * Request from the server the list of pipelines
   */
  _loadPipelinesFromServer: function() {
    
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: true,
      ifModified: true,
      contentType: "application/json; charset=UTF-8",
      success: function(data,text,res) {
        
        if (res.status === 200) {
          // change DOM only if 200, ignoring 304
          this.setState({data: data, status: '200', statusText: ''});
        }

      }.bind(this),

      error: function(xhr, status, err) {
        this.setState({
                        data:[], 
                        status: xhr.status,
                        statusText: xhr.responseText
                      });
      }.bind(this)

    });
  },

  getInitialState: function() {
    return {data: [], status: '200', statusText: ''};
  },

  componentDidMount: function() {
    this._loadPipelinesFromServer();
    setInterval(this._loadPipelinesFromServer, this.props.pollInterval);
  },

  render: function() {
    return (
      <div className="concourse-radiator">
        <h1>ConcourseCI Builds</h1>
        <PipelineList data={this.state.data} status={this.state.status} statusText={this.state.statusText} />
      </div>
    );
  }
});

/**
 * The list of all the pipelines
 */
var PipelineList = React.createClass({

  render: function() {

    var commentNodes = '';

    // if there is an error on the proxy server, then show the Error message
    if (this.props.status == "500") {
      commentNodes = (
        <div id="error-block">
          <img id="error-image" src="/images/buckleup.svg" />
          <h1>{this.props.statusText}</h1>
        </div>
      )
    }
    // otherwise, make a list of pipelines
    else if (this.props.data.length > 0) {
      commentNodes = this.props.data.map(function(pipeline) {
        return (
          <Pipeline key={pipeline.name} name={pipeline.name} url={pipeline.url} paused={pipeline.paused} jobs={pipeline.jobs} />
        );
      });
    }

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