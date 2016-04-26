var React = require('react');
var ReactDOM = require('react-dom');
var SurveyAccess = require('./SurveyAccess');

module.exports = function(container, props) {
    ReactDOM.render(<SurveyAccess {...props} />, container);
};