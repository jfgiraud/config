#!/usr/bin/perl -w
$|=1 ;

use strict ;
use Getopt::Long;
use utf8;

Getopt::Long::Configure(qw{no_auto_abbrev no_ignore_case_always});

my $use_regexp;
my $search=undef;
my $replace=undef;
my $simulate=0;
my $confirm=0;
my $extract_map=0;
my $apply_map=0;
my $debug=0;

GetOptions ('search|s=s' => sub { $use_regexp=0; $search=$_[1] },
	    'search-regex|S=s' => sub { $use_regexp=1; $search=$_[1] },
	    'replace|r=s' => \$replace,
	    'simulate|t' => \$simulate,
	    'confirm|c' => \$confirm,
	    'extract-map|e' => \$extract_map,
	    'apply-map|a' => \$apply_map,
	    'debug|d' => \$debug
);

if ($debug) {
    print STDERR "search: $search" . ($use_regexp ? " (regex)" : " (fixed)") . "\n";
    print STDERR "replace: $replace\n";
    print STDERR "simulate: $simulate\n";
}

sub error($$) {
    my ($status, $msg) = @_;
    print STDERR "$msg\n";
    exit($status);
}

error(1,"setting option --simulate makes no sense with option --extract-map") if ($extract_map && $simulate);
error(1,"setting option --confirm makes no sense with option --extract-map") if ($extract_map && $confirm);
error(1,"--extract-map and --apply-map option are mutually exclusives") if ($extract_map && $apply_map);
error(1,"setting option --extract-map implies to set options --search and --replace") if ($extract_map && ((not defined $search) || (not defined $replace)));
exit 1;

