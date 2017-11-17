#!/usr/bin/perl
#read in a tab delimited file of uniprot ids and call pfam with them. parse the results 
#to get domain info and spit that out to a new file that can be read into FM

use strict;
use warnings;

use LWP::UserAgent;
use XML::LibXML;

my $ua = LWP::UserAgent->new;
$ua->env_proxy;

open FILE, "C:/Users/jbelmont/Desktop/submit_file" or die $!;	#input file
open PFAM_A, ">PFAM_As";
open PFAM_B, ">PFAM_Bs";

while(!eof(FILE)){
	my $line=readline(FILE);
	chomp($line);
	my @tokens = split(/\t/,$line);
	my $ID=$tokens[0];
	my $seq=$tokens[1];
	###Submit the ID to pfam
	print "$ID\n";
	eval{
		my $res = $ua->get( 'http://pfam.sanger.ac.uk/protein?entry='.$ID.'&output=xml' );
		#create parser object and parse the incoming XML	
		my $xml = $res->content;
		my $xml_parser = XML::LibXML->new();
		my $dom = $xml_parser->parse_string( $xml );
		my $root = $dom->documentElement();
		my ( $entry ) = $root->getChildrenByTagName( 'entry' );
		my @matches = $entry->getElementsByTagName( 'matches' );
		my $matches = $entry->getAttribute( 'sequence' );
		print "\n\n\n\n$matches[0]\n\n\n\n";
		my @domain_ids = $matches[0] =~ m/id="[^"]*"/g;
		my @domain_types = $matches[0] =~ m/type="[^"]*"/g;
		my @domain_start = $matches[0] =~ m/\sstart="[0-9]*"/g;
		my @domain_end = $matches[0] =~ m/\send="[0-9]*"/g;
		#chop to remove last " from each array element
		chop(@domain_ids);
		chop(@domain_types);
		chop(@domain_start);
		chop(@domain_end);
		#loop through domain annotation arrays and write the results out to separate tab-delimited files for Pfam As and Bs
		foreach my $i(0..$#domain_ids){
			print "$domain_types[$i]\n";
			my $d_id = substr($domain_ids[$i],4);
			my $type = substr($domain_types[$i],6);
			my $start = substr($domain_start[$i],8);
			my $end = substr($domain_end[$i],6);
			print "$ID\t$d_id\t$type\t$start\t$end\n";
			if($type eq "Pfam-A"){
				print PFAM_A "$ID\t$d_id\t$start\t$end\n";
			} elsif ($type eq "Pfam-B"){
				print PFAM_B "$ID\t$d_id\t$start\t$end\n";
			} else {
				print "Error--unusual entry in type field\n";
			}
		}
	};
	if($@){
		print "error: failed to retrieve XML. This ID may be missing from the PFAM database. Submitting the sequence of $ID for domain prediction\n";
		open(TEMP,">","temp.seq");
		print TEMP $seq;
		#system("curl -H 'Expect:' -F seq='<temp.seq' -F output=xml http://pfam.sanger.ac.uk/search/sequence");		
		#my $xml = $res->content;
		#my $xml_parser = XML::LibXML->new();
		#my $dom = $xml_parser->parse_string( $xml );
		#my $root = $dom->documentElement();
		#my ( $entry ) = $root->getChildrenByTagName( 'entry' );
		#print 'accession: ' . $entry->getAttribute( 'accession' ) . "\n";
	}
	if($.%50==0){	#take a 10 min break after every 50 submissions
		sleep(600);
	}
}
print "All done!";