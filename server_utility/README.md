# server\_utility

## Description

Several scripts that can be used in conjunction with running dominions servers to send out emails and perform backups, with example dom4 server scripts as well

## Files

### emailUpdates.py

script purposed to send emails to players for reminders - best paired with cron and the dom4 option --postexec.

Requires:

A per-game tabulated list of the format <Nation>\t<email_address>

An accessible module mySMTP that provides the email authentication details


### teamOrg.py 

script purposed to do a ranking system, which we used for having some modicrum of matchmaking and team balancing

## Folders

examples/scripts

examples/savedgames
