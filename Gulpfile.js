var gulp = require('gulp');
var less = require('gulp-less');
var minifyCss = require('gulp-minify-css');
var browserify = require('browserify');
var reactify = require('reactify');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var uglify = require('gulp-uglify');

gulp.task('default', ['build']);
gulp.task('build', ['app', 'styles']);

gulp.task('app', function() {
    return browserify({
        entries: ['./client/js/index.js'],
        transform: [reactify],
        standalone: 'anonymonkey_authority'
    })
    .bundle()
    .pipe(source('app.js'))
    .pipe(gulp.dest('anonymonkey_authority/static/'));
});

gulp.task('styles', function() {
    return gulp.src('client/styles.less')
        .pipe(less())
        .pipe(minifyCss())
        .pipe(gulp.dest('anonymonkey_authority/static/'));
});