#!/usr/bin/env python
#
#  Copyright (C) 2006  Martin Blais <blais at furius dot ca>
#  2008-02: Improvements by "Giovanni Bajo" <rasky at develer dot com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""svndumpfilter3 [<options>] [<path> ...]

A rewrite of Subversion's svndumpfilter in pure Python, that allows you to
untangle move/copy operations between excluded and included sets of files/dirs,
by converting them into additions.  If you use this option, it fetches the
original files from a given repository.



.. important::

   Some people have been reporting a bug with this script, that it will create
   an empty file on a large repository.  It worked great for the split that I
   had to do on my repository, but I have no time to fix the problem that occurs
   for some other people's repositories (I really, really do not have the time
   to work on this).  If you find the glitch, please send me a patch.  I think
   the problem is likely to be a minor one.  If you need this for your business
   and you're willing to pay hourly rates, I might be able to find someone to
   work on it (perhaps me (http://furius.ca/home/consulting.html), depending on
   schedule).



The list of <path> paths are the paths to filter in the repository.  You pipe
the dumpfile through stdin.  If you want to untangle the copy operations, you
need a live repository and to use --untangle=REPOS_PATH.  Like this::

  cat dumpfile | svndumpfilter3 --untangle=/my/svnroot project1 project2

The paths can include wildcards, and can consist of multiple parts, like::

  cat dumpfile | svndumpfilter3 tags/proj.*/subproj trunk/subproj

Each component of the path is seperated and matched separately (hence the above
would match for instance tags/proj-1.2/subproj but not tags/proj-1.2/a/subproj).

.. note::

    This script's interface is only slightly different than Subversion's
    svndumpfilter, it does not take subcommands; its default behaviour is that
    of the 'include' subcommand of svndumpfilter.  If you need 'exclude'
    behaviour, just invoke it with the --exclude option.

This is useful if you want to split a repository for which files have been
copied or moved between filtered and non-filtered locations.  The resulting dump
would be illegal if we just ignored these, because Subversion records the
copy/move operations only.

Chapter 5 hints about this, for more details about the problem, see there:

  Also, copied paths can give you some trouble. Subversion supports
  copy operations in the repository, where a new path is created by
  copying some already existing path. It is possible that at some
  point in the lifetime of your repository, you might have copied a
  file or directory from some location that svndumpfilter is
  excluding, to a location that it is including. In order to make
  the dump data self-sufficient, svndumpfilter needs to still show
  the addition of the new path including the contents of any files
  created by the copy-and not represent that addition as a copy from
  a source that won't exist in your filtered dump data stream. But
  because the Subversion repository dump format only shows what was
  changed in each revision, the contents of the copy source might
  not be readily available. If you suspect that you have any copies
  of this sort in your repository, you might want to rethink your
  set of included/excluded paths.


Future Work
-----------

* We still need to implement the per-subcommand options of svndumpfilter.  Feel
  free to do so if you need it, or contact Martin Blais for subcontracting (I
  will do this for money, right now I have no time).

Credits
-------

This code is originally based on Simon Tatham's svndumpfilter2, but we
significantly changed the main loop and are using 'svnadmin dump' to fetch old
revisions rather than working recursively with 'svnlook cat'.  The problem I was
having was that svndumpfilter2 was running out of memory so I had to rewrite it.

svndumpfilter2 tracks all files itself in order to replicate the required
revisions, and it uses ``svnlook cat`` to fetch them, which is fast.  This
consumes a lot of memory (I could not run it on a 126MB repository with 2800
revisions on my P4 1GB RAM server).  svndumpfilter3 does not track the revisions
itself, instead it uses ``svnadmin dump`` with the original svndumpfilter to
produce the necessary lumps to insert them in the output.  This operation is
much slower, but it does not matter if you have relatively few move/copy
operations between excluded directories, which I think is by far the common case
for multiple project roots (it was my case).

[2009-01-08] An bugfix patch was provided by Jamie Townsend <jtownsen at
progress dot com>.

[2009-04-05] Minor path matching improvements by Matthias Troffaes <matthias
dot troffaes at gmail dot com>

[2012-02-21] A few fixes  from "Bernhard M. Wiedemann" <bwiedemann dot
suse at de> were applied.

[2012-06-16] More fixed from "Bernhard M. Wiedemann" <bwiedemann dot
suse at de> were applied; Bernard mentions: "this helped produce 100% identical
results for our split of a 4GB dump." so I applied confidently without testing.
More details at his copy: https://github.com/bmwiedemann/svndumpfilter3

[2012-12-22] Bug fix submitted by Jeppe Oeland on explicit usage of 'md5' for 
hashlib.

Important Note
--------------

I cannot guarantee anything about your data (see the legal terms above).  If you
lose data by using this program, THAT IS YOUR OWN PROBLEM.  Do not forget to
MAKE BACKUPS in case something goes wrong.  This is your own responsibility.
Always make backups.


[2009-09-18]
Here is a note from a user about a potential problem with the preservation of
properties, with the >100 hr/week workload, I have no time to look into it at
the moment:

  From "Fldvri Gyrgy"
  To  	blais@furius.ca
  Subject  	Critical bug in svndumpfilter3? 	Show full header
  Hello Martin,

  First of all, your tool helped me a lot in my task. But I think I have
  found a critical bug in svndumpfilter3 which can cause loss of
  revisioned properties. Please check it and distribute a fix if you have
  time.

  I experienced that some files and folders lost their revisioned
  properties after filtering them by svndumpfilter3. It was not some of
  the properties, but all of them, and I have not found any pattern at
  first. By comparing the input and output dumps I realized, that the
  problem occures with files/folders which has modifications committed.

  The root cause is that if a modification does not tough the properties,
  the lump of that change will not contain properties section at all, but
  svndumpfilter3 will add an empty one anyway. But this empty properties
  section means, that properties has been modified, and after modification
  there are no porperties anymore.

  I propose something like this: during read of lump check if there were
  properties section read at all, and use this info to decide if it should
  be written.

"""

## FIXME: TODO, incorporate change from Barry Warsaw:
##
##   I did make one small change though.  InterestingPaths.interesting()
##   seems more useful to me just doing a straight up regexp match instead
##   of trying to split the path and matching against the first
##   component.  I'm not quite sure how useful the default behavior would
##   be actually.  So I made a change to something like this:
##
##   for r in self.res:
##       if r.match(path):
##           r = True
##           break
##   else:
##       r = False
##   ...
##
##   So I could do something like
##
##   ... | svndumpfilter3 --exclude /staging/.* > ...
##
##   or more complicated regexps.  Anyway, again thanks and hope all is well.
##
##   --Barry
##

## A note about locale From Doug Hunley
## ------------------------------------
##
## I've been seeing the issue w/ svndumpfilter3 where the dump that is
## created contains all the relevant revisions but no actual data. In my
## case, it turns out that doing:
## export LC_CTYPE=en_US.UTF-8
## and /then/ running svndumpfilter3 worked.
##
## When I tried to to checkout a copy of the repo I was using to
## 'untangle' things I found that the checkout failed with an error about
## being unable to convert string to native encoding, which when googled,
## led me to a page saying to set the above. Doing so let me check out
## the repo in question, so I then re-ran svndumpfilter and got a useable
## dmp file.
##
##  --Doug


__author__ = 'Martin Blais <blais@furius.ca>'
__author_orig__ = 'Simon Tatham (svndumpfilter2)'
__contributors__ = ('Martin Blais <blais@furius.ca>',
                    'Matthias Troffaes <matthias.troffaes@gmail.com>',)


import sys
if sys.version_info[:2] < (2, 4):
    raise SystemExit("Error: You need Python 2.4 or over.")

# stdlib imports
import os, re, string, hashlib, warnings
from os.path import basename
from subprocess import Popen, PIPE



# Constants for versions.
# Note: v3 does not really exist, see this for details:
# http://svn.haxx.se/dev/archive-2004-11/1111.shtml
__supported_versions__ = ('2', '3')

fmtequiv = {'1': 1,
            '2': 2,
            '3': 2}

format_warning = False


# Note
# ----
# We expect to be reading a valid SVN dump file output by SVN
# itself, so I currently feel no particular obligation to do
# user-friendly error reporting. Assertion failures or Python
# exceptions are perfectly adequate, since errors should only show
# up during development of this script.

# The sensible way to deal with a pathname is to split it into pieces at the
# slashes and thereafter treat it as a list.  The following functions provide
# that functionality.
# Note: from Simon Tatham.
def splitpath(s):
    """
    Split a string path into a path-as-list (a list of its components).
    """
    thelist = string.split(s, "/")
    # Simplest way to remove all empty elements!
    try:
        while 1:
            thelist.remove("")
    except ValueError:
        pass
    return thelist

def joinpath(thelist, prefix=""):
    """
    Convert a path-as-list into a string.
    """
    return prefix + string.join(thelist, "/")

def catpath(path1, path2, prefix=""):
    """
    Concatenate two paths, return a path as a string.
    """
    return joinpath(splitpath(path1) + splitpath(path2), prefix)


# Note: from Simon Tatham.
class InterestingPaths:
    """
    Decide whether a pathname is interesting or not.
    """
    def __init__(self, args, reverse):
        self.reverse = reverse
        """True if we should reverse the matches, e.g. true means exclude on the
        list of paths rather than include."""

        self.res = []
        for a in args:
            self.res.append([])
            for component in splitpath(a):
                self.res[-1].append(re.compile('^' + component + '$'))
        """List of regular expressions to match against/exclude."""

    def interesting(self, path):
        """
        Return true if this path is considered included.
        """
        match = False
        acomps = splitpath(path)
        assert len(acomps) > 0
        for rcomps in self.res:
            # if rcomps has more components than acomps
            # then we  cannot have a match, so skip this case
            if len(rcomps) > len(acomps):
                continue
            # see if rcomps matches acomps
            for r, a in zip(rcomps, acomps):
                if not r.match(a):
                    break
            else:
                # everything matches
                match = True
                break
        if self.reverse:
            match = not match
        return match


# Note: from Simon Tatham.
class Lump:
    """
    A class and some functions to handle a single lump of
    RFC822-ish-headers-plus-data read from an SVN dump file.
    """
    def __init__(self):
        self.hdrlist = []
        self.hdrdict = {}
        self.prop = ""
        self.text = ""
        self.proplist = []
        self.propdict = {}

    def sethdr(self, key, val):
        """
        Set header 'key' to 'val'.
        """
        if not self.hdrdict.has_key(key):
            self.hdrlist.append(key)
        self.hdrdict[key] = val

    def delhdr(self, key):
        """
        Delete the header 'key'.
        """
        if self.hdrdict.has_key(key):
            del self.hdrdict[key]
            self.hdrlist.remove(key)

    def propparse(self):
        """
        Parse the properties of the lump.
        """
        index = 0
        while 1:
            if self.prop[index:index+2] == "K ":
                wantval = 1
            elif self.prop[index:index+2] == "D ":
                wantval = 0
            elif self.prop[index:index+9] == "PROPS-END":
                break
            else:
                raise "Unrecognised record in props section"
            nlpos = string.find(self.prop, "\n", index)
            assert nlpos > 0
            namelen = string.atoi(self.prop[index+2:nlpos])
            assert self.prop[nlpos+1+namelen] == "\n"
            name = self.prop[nlpos+1:nlpos+1+namelen]
            index = nlpos+2+namelen
            if wantval:
                assert self.prop[index:index+2] == "V "
                nlpos = string.find(self.prop, "\n", index)
                assert nlpos > 0
                proplen = string.atoi(self.prop[index+2:nlpos])
                assert self.prop[nlpos+1+proplen] == "\n"
                prop = self.prop[nlpos+1:nlpos+1+proplen]
                index = nlpos+2+proplen
            else:
                prop = None
            self.proplist.append(name)
            self.propdict[name] = prop

    def setprop(self, key, val):
        """
        Set property 'key' to 'val'.
        """
        if not self.propdict.has_key(key):
            self.proplist.append(key)
        self.propdict[key] = val
        self.hasprop = True

    def delprop(self, key):
        """
        Delete property 'key'.
        """
        if self.propdict.has_key(key):
            del self.propdict[key]
            self.proplist.remove(key)

    def correct_headers(self):
        """
        Adjust the headers, from updated contents.
        """
        # First reconstitute the properties block.
        self.prop = ""

        # JT if there's a delete of something that got added in the same transaction
        #    (ie, it was added and then renamed), there must be no properties created for it
        #if not opts.prune_properties or len(self.proplist) > 0:
        if (not opts.prune_properties or len(self.proplist) > 0) and self.hdrdict.get('Node-action') != "delete":
            for key in self.proplist:
                val = self.propdict[key]
                if val is None:
                    self.prop += "D %d\n%s\n" % (len(key), key)
                else:
                    self.prop += "K %d\n%s\n" % (len(key), key)
                    self.prop += "V %d\n%s\n" % (len(val), val)
            if self.hasprop:
                self.prop = self.prop + "PROPS-END\n"

        # Now fix up the content length headers.
        if len(self.prop) > 0:
            self.sethdr("Prop-content-length", str(len(self.prop)))
        else:
            self.delhdr("Prop-content-length")

        if self.hastext and len(self.text) >= 0 or \
           (self.hdrdict.get('Node-action', None) == 'add' and
            self.hdrdict.get('Node-kind', None) == 'file' and
            not self.hdrdict.get('Node-copyfrom-path', None)):

            self.sethdr("Text-content-length", str(len(self.text)))
            m = hashlib.new('md5')
            m.update(self.text)
            self.sethdr("Text-content-md5", m.hexdigest())
        else:
            self.delhdr("Text-content-length")
            self.delhdr("Text-content-md5")

        if len(self.prop) > 0 or len(self.text) > 0:
            self.sethdr("Content-length", str(len(self.prop)+len(self.text)))
        else:
            self.delhdr("Content-length")


format_re = re.compile('SVN-fs-dump-format-version: (\d+)\s*$')
uuid_re = re.compile('UUID: ([0-9a-fA-F\-]+)\s*$')

def read_dump_header(f):
    """
    Match and read a dumpfile's header and return the format versin and file's
    UUID.
    """
    mo_version = format_re.match(f.readline())
    assert mo_version
    f.readline()
    mo_uuid = uuid_re.match(f.readline())
    assert mo_uuid
    f.readline()

    text = '%s\n%s\n' % (mo_version.string, mo_uuid.string)
    return mo_version.group(1), mo_uuid.group(1), text


header_re = re.compile('([a-zA-Z0-9\-]+): (.*)$')

# Note: from Simon Tatham.
def read_rfc822_headers(f):
    """
    Read a set of RFC822 headers from the given file.  We return a dict and the
    set of original lines that were parsed to obtain the contents.
    """
    ret = Lump()

    lines = []
    while 1:
        s = f.readline()
        if not s:
            return None, [] # end of file

        # Watch for the newline char that ends the headers.
        if s == '\n':
            if len(ret.hdrlist) > 0:
                break # newline after headers ends them
            else:
                continue # newline before headers is simply ignored

        lines.append(s)

        mo = header_re.match(s)
        if mo is None:
            raise SystemExit("Error: Parsing header: %s" % s)

        ret.sethdr(*mo.groups())

    return ret, lines

# Note: from Simon Tatham.
def read_lump(f):
    """
    Read a single lump from the given file.

    Note: there is a single empty line that is used to conclude the RFC headers,
    and it is not part of the rest.  Then you have the properties, which are of
    exactly the property length, and right away follows the contents of exactly
    the length of the content length.  Then follows two newline characters and
    then the next lump starts.
    """
    lump, lines = read_rfc822_headers(f)
    if lump is None:
        return None
    pcl = int(lump.hdrdict.get("Prop-content-length", "-1"))
    tcl = int(lump.hdrdict.get("Text-content-length", "-1"))
    lump.hasprop = pcl >= 0
    if lump.hasprop:
        lump.prop = f.read(pcl)
        lump.propparse()
    lump.hastext = tcl >= 0
    if lump.hastext:
        lump.text = f.read(tcl)

    lump.orig_text = os.linesep.join(lines) + lump.prop + lump.text

    return lump


def write_lump(f, lump):
    """
    Write a single lump to the given file.
    """
    # Make sure that the lengths are adjusted appropriately.
    lump.correct_headers()
    for key in lump.hdrlist:
        val = lump.hdrdict[key]
        f.write(key + ": " + val + "\n")
    f.write("\n")

    # Render the payload.
    f.write(lump.prop)
    f.write(lump.text)

    # Add newlines at the end of chunks, for readers.
    f.write('\n')
    if not lump.hdrdict.has_key("Revision-number"):
        f.write('\n')


def fetch_rev_rename(repos, srcrev, srcpath, path, fout, flog, format):
    """
    Dumps 'srcpath' at revision 'srcrev' from repository 'repos',
    renaming the root of all the paths in it to 'path', and
    outputting the lumps in 'fout' (without the header and revision
    lump).
    """
    assert isinstance(srcrev, int)

    # Must find the source node, as it existed in the given revision, and copy
    # it in full.
    cmd = ('svnadmin', 'dump', '-r', str(srcrev), opts.repos)
    cmd_filter = ('svndumpfilter', 'include', srcpath)
    if opts.debug:
        print >> flog, ("Running command: '%s | %s'" %
                        (' '.join(cmd), ' '.join(cmd_filter)))
    fnull = open(os.devnull, 'w')
    p1 = Popen(cmd, stdout=PIPE, stderr=fnull)
    p2 = Popen(cmd_filter, stdin=p1.stdout,
               stdout=PIPE, stderr=fnull)
    fs = p2.stdout

    #
    # Process the subdump.
    #

    # Read and drop dump header.
    format_sub, uuid_sub, text_sub = read_dump_header(fs)

    global format_warning
    if fmtequiv[format] != fmtequiv[format_sub] and not format_warning:
        warnings.warn("Warning: Dump format is different than "
                      "the version of Subversion used to convert "
                      "move/copy into adds.")
        format_warning = True

    # Read and drpo the revision.
    lump_sub = read_lump(fs)
    assert lump_sub is not None
    assert lump_sub.hdrdict.has_key('Revision-number')

    while 1:
        # Read one lump at a time
        lump_sub = read_lump(fs)
        if lump_sub is None:
            break # At EOF

        # Make sure all the rest are file/dir lumps.
        assert not lump_sub.hdrdict.has_key('Revision-number')

        # Translate filename to its new location.
        path_sub = lump_sub.hdrdict['Node-path']
        assert path_sub.startswith(srcpath)
        path_sub_new = path + path_sub[len(srcpath):]
        lump_sub.sethdr('Node-path', path_sub_new)
        print >> flog, ("%s:    Converted  '%s' to '%s'" %
                        (progname, path_sub, path_sub_new))

        if path_sub_new == path:
            print >> flog, ("%s:    Marked '%s' as untangled." %
                            (progname, path))

            lines = ("Node-copyfrom-path: %s" % srcpath,
                     "Node-copyfrom-rev: %d" % srcrev)
            lump_sub.setprop('svn:untangled', "\n".join(lines))

        write_lump(fout, lump_sub)

    p2.wait()
    if p2.returncode != 0:
        raise SystemExit("Error: Running %s" % " ".join(cmd))


def parse_options():
    """
    Parse and validate the options.
    """
    global progname
    progname = basename(sys.argv[0])

    import optparse
    parser = optparse.OptionParser(__doc__.strip())

    # Original svndumpfilter options.
    #
    # FIXME: we still need to implement these 3 options.
    #
    # FIXME: we could convert this script to use subcommands and add the same
    # subcommand options that are present in svndumpfilter.
    parser.add_option('--drop-empty-revs', action='store_true',
                      help="Remove revisions emptied by filtering.")
    parser.add_option('--renumber-revs', action='store_true',
                      help="Renumber revisions left after filtering.")
    parser.add_option('--preserve-revprops', action='store_true',
                      help="Don't filter revision properties.")


    parser.add_option('--quiet', action='store_true',
                      help="Do not display filtering statistics.")

    parser.add_option('-e', '--exclude', action='store_true',
                      help="The given paths are to be excluded rather than "
                      "included (the default is to include).")

    parser.add_option('-p', '--prune-properties', action='store_true',
                      help="Prune empty properties if empty. This makes the "
                           "dump file smaller, but does not match latest "
                           "version of svnadmin dump, so don't use if e.g. "
                           "you want to diff the input and output dump.")

    parser.add_option('-u', '--untangle', action='store', dest='repos',
                      metavar='REPOS_PATH',
                      help="If True, convert move/copy from filtered paths "
                      "to additions.  You need to specify the repository to "
                      "fetch the missing files from.")

    parser.add_option('-n', '--no-filter', action='store_true',
                      help="Do not actually apply filters, but just "
                      "perform the requested conversions.  This can be used "
                      "as a test by running the output into svndumpfilter, "
                      "which should now succeed.")

    parser.add_option('-k', '--ignore-missing', action='store_true',
                      help="Continue as much as possible after an error due to "
                      "a missing file.  If such errors are present, the "
                      "resulting noutput dump may not be usable (files will be "
                      "missing.  The original svndumpfilter actually exits "
                      "when this occurs (this is our default behaviour as "
                      "well).  You can use this to view the list of files "
                      "that are missing by using the specified filter.")

    parser.add_option("--filter-contents", type="string", nargs=3, default=[],
                      action="append", metavar="RX_FILES RX_MATCH SUB",
                      help="Apply a regular expression substitution (filter) "
                           "to the contents of a certain set of files. This "
                           "option needs three arguments (separated by "
                           "spaces): a regular expression that specifies the "
                           "files to be processed (eg: \"*.[ch]\"); the regexp "
                           "that matches the text; the replacement regexp. You "
                           "can specify this option as many times as you need.")

    parser.add_option("--filter-logs", type="string", nargs=2, default=[],
                      action="append", metavar="RX_MATCH SUB",
                      help="Apply a regular expression substitution (filter) "
                           "to the commit log messages. This "
                           "option needs two arguments (separated by "
                           "spaces): the regexp "
                           "that matches the text; the replacement regexp. You "
                           "can specify this option as many times as you need.")

    parser.add_option("--skip-rev", type="int", action="append", default=[],
                      metavar="REV",
                      help="Skip (filter out) a specific revision. You can "
                           "specify this option as many times as you need.")

    parser.add_option('--debug', action='store_true',
                      help=optparse.SUPPRESS_HELP)

    global opts
    opts, args = parser.parse_args()

    # Args can be empty. In that case, we will not do any path-based filtering
    # (= all paths are included).
    inpaths = args

    # Validate filter regular expressions
    try:
        opts.filter_contents = [(re.compile(a), re.compile(b), c)
                                for a,b,c in opts.filter_contents]
        opts.filter_logs = [(re.compile(a), b)
                            for a,b in opts.filter_logs]
    except Exception, e:
        parser.error("error parsing regular expression: %s" % str(e))

    if opts.no_filter and not opts.repos:
        parser.error("Both filtering and untangle are disabled.  "
                     "This filter will have no effect.")

    if opts.repos and opts.ignore_missing:
        parser.error("You don't need --ignore-missing if you're untangling.")

    opts.skip_rev = set(opts.skip_rev)

    for optname in 'drop-empty-revs', 'renumber-revs', 'preserve-revprops':
        if getattr(opts, optname.replace('-', '_')):
            parser.error("(Option '%s' not implemented)." % optname)

    return opts, inpaths

def main():
    """
    Main program that just reads the lumps and copies them out.
    """
    opts, inpaths = parse_options()

    # Open in and out files.
    fr = sys.stdin
    fw = sys.stdout
    flog = sys.stderr

    # Track which base files are interesting, accepting regexps for input
    # filenames.
    if opts.exclude:
        print >> flog, 'Excluding prefixes:'
    else:
        print >> flog, 'Including prefixes:'
    for p in inpaths:
        print >> flog, "   '/%s'" % p
    print >> flog
    if not inpaths:
        opts.exclude = True

    paths = InterestingPaths(inpaths, opts.exclude)

    # Read the dumpfile header.
    format, uuid, text = read_dump_header(fr)
    fw.write(text)

    if format not in __supported_versions__:
        # Note: you could update this script easily to support other formats, it
        # will probably be trivial to do so.
        raise SystemExit("Error: dump file in format '%s' not supported." %
                         format)

    filtered = set()
    """Set of filtered paths."""

    converted = []
    """List of (srcpath, destpath, type, rev) tuples that describe the paths
    that were converted from move/copy into additions."""

    skipping = False
    """True while we are skipping a revision."""

    # Process the dump file.
    while 1:
        # Read one lump at a time
        lump = read_lump(fr)
        if lump is None:
            break # At EOF

        # Let the revisions pass through
        if lump.hdrdict.has_key('Revision-number'):

            revno = lump.hdrdict['Revision-number']
            if int(revno) in opts.skip_rev:
                print >> flog, 'Revision %s filtered out.' % revno
                skipping = True
                continue

            skipping = False

            # Filter svn:log property
            # JT Revision 0 may not have an svn:log entry, so we need do accommodate that
            #   (added if condition)
            if lump.hdrdict.has_key('svn:log'):
                log = lump.propdict["svn:log"]
                num_subs = 0
                for rx_search, sub in opts.filter_logs:
                    lump.propdict["svn:log"], subs = re.subn(rx_search, sub, lump.propdict["svn:log"])
                    num_subs += subs
                if num_subs:
                    print >> flog, "log filtered: %d times" % num_subs
                    lump.correct_headers()

            write_lump(fw, lump)
            if not opts.quiet:
                print >> flog, 'Revision %s committed as %s.' % (revno, revno)
            continue

        # If we're skipping this revision, go to the next lump
        if skipping:
            continue

        # Print some kind of progress information.
        if opts.debug:
            d = lump.hdrdict
            print >> flog, (
                '   %-10s %-10s %s' %
                (d.get('Node-kind', ''), d['Node-action'], d['Node-path']))

        # Filter out the uninteresting lumps
        path = lump.hdrdict['Node-path']
        if not paths.interesting(path):
            filtered.add(path)
            continue

        # See if any of the provided filters match against this file
        num_subs = 0
        for rx_file, rx_search, sub in opts.filter_contents:
            if rx_file.search(path):
                lump.text, subs = re.subn(rx_search, sub, lump.text)
                num_subs += subs
        if num_subs:
            print >> flog, "contents filtered: %d times" % num_subs
            lump.correct_headers()

        # If this is not a move/copy.
        if not lump.hdrdict.has_key("Node-copyfrom-path"):
            # Just pass through.
            write_lump(fw, lump)

        else:
            # This is a move/copy.
            srcrev = int(lump.hdrdict["Node-copyfrom-rev"])
            srcpath = lump.hdrdict["Node-copyfrom-path"]

            # Check if the copy's source comes from a filtered path.
            if paths.interesting(srcpath):
                # If it comes from an included path, just pass through.
                write_lump(fw, lump)

            else:
                # Otherwise we deal with the case where the source comes from a
                # filtered path.
                if not opts.repos:
                    msg = ("%s: Invalid copy source path '%s'" %
                           (progname, srcpath))
                    if opts.ignore_missing:
                        print >> flog, msg
                        continue
                    else:
                        raise SystemExit(msg)

                converted.append(
                    (srcpath, path, lump.hdrdict['Node-kind'], srcrev))

                print >> flog, ("%s: Converting '%s' to a copy on '%s'" %
                                (progname, srcpath, path))

                # Fetch the old revision from the repository.
                fetch_rev_rename(opts.repos, srcrev, srcpath, path,
                                 fw, flog, format)

                # We also check if the original lump includes a payload, and if
                # it does, we need to add a change record providing the new
                # contents.
                if len(lump.text) > 0 and paths.interesting(path):
                    print >> flog, ("%s:    Added a change record for '%s' as "
                                    "well.") % (progname, path)
                    lump.sethdr("Node-action", "change")
                    lump.delhdr("Node-copyfrom-rev")
                    lump.delhdr("Node-copyfrom-path")
                    write_lump(fw, lump)

    fr.close()
    fw.close()

    if not opts.quiet:
        # Print summary of dropped nodes.
        print >> flog, 'Dropped %d node(s):' % len(filtered)
        for path in sorted(filtered):
            print >> flog, "   '/%s'" % path
        print >> flog

        # Print summary of converted nodes.
        print >> flog, '%s nodes converted into additions(s).' % len(converted)
        for srcpath, dstpath, typ, srcrev in sorted(converted):
            print >> flog, ("   '/%s' to '/%s' (%s, revision %s)" %
                            (srcpath, dstpath, typ, srcrev))
        print >> flog


if __name__ == '__main__':
    main()
