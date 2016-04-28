var React = require('react');
var jwtDecode = require('jwt-decode');
var request = require('superagent');
var createHash = require('crypto').createHash;
var swal = require('sweetalert');

var SurveyAccess = React.createClass({
    getInitialState: function() {
        return {
            token: null,
            decoded_token: null,
            h: null,
            userValue: null,
            c: null,
            anonymous_token: null,
            decoded_anonymous_token: null,
            inner_token: null,
            c_digest: null,
            token_hash: null,
            survey_id: null
        }
    },

    componentDidMount: function() {
        this.setState({
            token: this.props.token,
            decoded_token: JSON.stringify(jwtDecode(this.props.token), null, ' ')
        });

        request.post('/api/tokens/initialize')
            .send({survey_token: this.props.token})
            .end(function(err, res) {
                if (err) {
                    swal('Token error', 'Failed to validate email token. Maybe it has already been used.', 'error');
                    return;
                }
                this.setState({h: res.body.h});
            }.bind(this));
    },

    onUserValue: function(ev) {
        var value = ev.target.value;
        this.setState({userValue: value});
    },

    fetchToken: function() {
        request.post('/api/tokens/authorize')
            .send({
                survey_token: this.state.token,
                value: this.state.userValue
            })
            .end(function(err, res) {
                if (err) {
                    swal('Token error', 'Unable to fetch anonymous token. Maybe it has already been fetched.', 'error');
                    return;
                }
                console.log(res.body.c + this.state.userValue);
                this.setState({
                    anonymous_token: res.body.token,
                    decoded_anonymous_token: JSON.stringify(jwtDecode(res.body.token), null, ' '),
                    c: res.body.c,
                    inner_token: jwtDecode(res.body.token).token,
                    survey_id: jwtDecode(res.body.token).survey_id
                });
                var sha256 = createHash('sha256');
                this.setState({c_digest: sha256.update(res.body.c).digest('hex')});
                var sha256 = createHash('sha256');
                this.setState({token_hash: sha256.update(res.body.c + this.state.userValue).digest('hex')});
            }.bind(this));
    },

    render: function() {
        var answerButton = null;
        if (this.state.survey_id && this.state.anonymous_token) {
            answerButton = (
                <div>
                    <h3>Answer survey</h3>
                    <a
                        href={jwtDecode(this.state.anonymous_token).aud + '/survey/' + this.state.survey_id + '?token=' + this.state.anonymous_token}
                        className="btn btn-success">
                        Answer survey
                    </a>
                </div>
            );
        }

        return (
            <div>
                <h3>User access token</h3><hr />
                <div className="row">
                    <div className="col-md-6">
                        <b>Token: </b>
                        <textarea rows="5" className="form-control" value={this.state.token} />
                    </div>
                    <div className="col-md-6">
                        <b>Decoded: </b>
                        <textarea rows="5" className="form-control" value={this.state.decoded_token}/>
                    </div>
                </div>

                <h3>Handshake hash</h3><hr />
                <span><b>Hash:</b> {this.state.h}</span>

                <h3>User input</h3><hr />
                <input type="text" className="form-control" placeholder="Enter random value here" value={this.state.userValue} onChange={this.onUserValue} />
                <button className="btn btn-primary" onClick={this.fetchToken}>Grab unique token</button>

                <h3>Anonymous token</h3>
                <div className="row">
                    <div className="col-md-4">
                        <b>Token</b>
                        <textarea rows="5" className="form-control" value={this.state.anonymous_token} />
                    </div>
                    <div className="col-md-4">
                        <b>Decoded</b>
                        <textarea rows="5" className="form-control" value={this.state.decoded_anonymous_token} />
                    </div>
                    <div className="col-md-4">
                        <b>Anonymous proof</b>
                        <p>
                            <b>c = </b> {this.state.c}<br />
                            <b>h = </b>SHA256(c) = SHA256({this.state.c}) = {this.state.c_digest}<br />
                            <b>token = </b>SHA256(c || value) = SHA256 ({this.state.c} || {this.state.userValue}) = {this.state.token_hash}
                        </p>
                    </div>
                </div>

                {answerButton}
            </div>
        )
    }
});

module.exports = SurveyAccess;