#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pedro Tome <Pedro.Tome@idiap.ch>
#
# Copyright (C) 2015 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This script evaluates the score files per user."""

import sys
import argparse
import bob.io.base
import bob.measure
import bob.io.matlab

import numpy, math
import os
from facereclib import utils

# matplotlib stuff
import matplotlib; matplotlib.use('pdf') #avoids TkInter threaded start
import matplotlib.pyplot as mpl
from matplotlib.backends.backend_pdf import PdfPages

# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)
# increase the default font size
matplotlib.rc('font', size=18)



def command_line_arguments(command_line_parameters):
  """Parse the program options"""

  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-d', '--dev-files', required=True, nargs='+', help = "A list of score files of the development set.")
  parser.add_argument('-e', '--eval-files', nargs='+', help = "A list of score files of the evaluation set; if given it must be the same number of files as the --dev-files.")
  parser.add_argument('-n', '--norm', default = 'norm', choices = ('nom', 'none'), help = "The scores are normalized in the rank [0,1].")
  parser.add_argument('-s', '--directory', default = '.', help = "A directory, where to find the --dev-files and the --eval-files")
  parser.add_argument('-c', '--criterion', default = 'EER', choices = ('EER', 'HTER'), help = "If given, the threshold of the development set will be computed with this criterion.")
  
  parser.add_argument('-P', '--pdf', required=True, help = "If given, Fauna graph will be plotted into the given pdf file.")
  parser.add_argument('-p', '--parser', default = '4column', choices = ('4column', '5column'), help="The style of the resulting score files. The default fits to the usual output of FaceRecLib score files.")

  parser.add_argument('--self-test', action='store_true', help=argparse.SUPPRESS)

  utils.add_logger_command_line_option(parser)

  # parse arguments
  args = parser.parse_args(command_line_parameters)

  utils.set_verbosity_level(args.verbose)

  # some sanity checks:
  if args.eval_files and len(args.dev_files) != len(args.eval_files):
    utils.error("The number of --dev-files (%d) and --eval-files (%d) are not identical" % (len(args.dev_files), len(args.eval_files)))

  return args

def _plot_scores(figsize, args, totalModels, ids_group, group, title):
  figure = mpl.figure(figsize=figsize)
  
  eer_mean = []
  thr_mean = [] 
  print("List of the non zero EER Models:")
  for model in range(len(totalModels)):
    
    scores = ids_group[ids_group[:,0] == totalModels[model], :]
    scoresTarget = scores[scores[:,4]=='1',3].astype(numpy.float64)
    scoresNonTarget = scores[scores[:,4]=='0',3].astype(numpy.float64)
    
    # compute threshold on development set
    threshold = {'EER': bob.measure.eer_threshold, 'HTER' : bob.measure.min_hter_threshold} [args.criterion](scoresNonTarget, scoresTarget)
    thr_mean.append(threshold)
    # apply threshold to development set
    far, frr = bob.measure.farfrr(scoresNonTarget, scoresTarget, threshold)
    #print("Model %s - The %s of the development set of '%s' is %2.3f%%" % (model, args.criterion, args.legends[i] if args.legends else args.dev_files[i], (far + frr) * 50.)) # / 2 * 100%
    eer = 100. * bob.measure.eer_rocch(scoresNonTarget, scoresTarget)
    eer_mean.append(eer)
    if (eer != 0):
      print("Model %s - The %s of the %s set is %2.3f%%" % (totalModels[model], args.criterion, group, eer )) # / 2 * 100%

    utils.info("Plotting Fauna graph to file '%s'" % args.pdf)
    # plot scoresTarget
    blue_dot,  = mpl.plot(numpy.ones(len(scoresTarget))*model, scoresTarget, 'bo')
    # plot scoresNonTarget        
    red_cross, = mpl.plot(numpy.ones(len(scoresNonTarget))*model, scoresNonTarget, 'rx')   
    # plot threshold
    black_th,  = mpl.plot(model, threshold, 'k*', markersize=16)
  
  # finalize plot
  offset = 0.01
  mpl.ylabel('Score norm')
  if (args.norm == 'none'):
    offset = numpy.mean(ids_group[:,3].astype(numpy.float64))/100
    mpl.ylabel('Score')

  mpl.axis([-1,len(totalModels), min(ids_group[:,3].astype(numpy.float64))-offset, max(ids_group[:,3].astype(numpy.float64))+offset])
  mpl.xticks(range(0,len(totalModels)+1,5))
  #mpl.xticks(range(0,len(totalModels),10), totalModels[range(0,len(totalModels),10)].astype(numpy.str), rotation = 'vertical')
  mpl.xlabel('User model')
  mpl.grid(True, color=(0.6,0.6,0.6))
  
  #thr_mean = {'EER': bob.measure.eer_threshold, 'HTER' : bob.measure.min_hter_threshold} [args.criterion](scores_dev[i][0], scores_dev[i][1])
  #mpl.axhline(y=thr_mean, xmin=0, xmax=1, c="blue", linewidth=1.5, zorder=0)
  
  #mpl.text(60, .025, r'$\mu=100,\ \sigma=15$')
  #mpl.annotate('local max', xy=(2, 1), xytext=(3, 1.5),arrowprops=dict(facecolor='black', shrink=0.05),)
  mpl.legend([blue_dot, red_cross, black_th], ["Target scores", "NonTarget scores", "Model threshold"], numpoints=1)
  mpl.legend(loc=5)
  #mpl.legend(handles = [blue_dot, red_cross, black_th],["Target scores", "NonTarget scores", "Model threshold"])
  
  mpl.title(title)

  return eer_mean, figure

def _plot_eer(figsize, eer, title):
  figure = mpl.figure(figsize=figsize)
  
  eermean = numpy.mean(eer)
  mpl.axhline(y=eermean, xmin=0, xmax=1, c="red", linewidth=1.5, zorder=0)
  legend_title = "System EER = %2.3f%%" % (eermean)
  mpl.legend([legend_title])

  # plot scoresTarget
  mpl.plot(range(len(eer)), eer, 'bo-')

  # finalize plot
  offset = 1
  mpl.axis([-1,len(eer), min(eer)-offset, max(eer)+offset])
  mpl.xticks(range(0,len(eer)+1,5))
  #mpl.annotate('EER mean', xy=(0, numpy.mean(eer)), xytext=(1, 3), arrowprops=dict(facecolor='black', shrink=0.05),)

  eerval = numpy.array(eer)
  eernonzero = eerval[eerval!=0]
  #import ipdb; ipdb.set_trace()
  #mpl.text(eerval.nonzero(), eernonzero,'u', horizontalalignment='center', verticalalignment='center')

  mpl.xlabel('User model')
  mpl.ylabel('EER (\%)')
  mpl.grid(True, color=(0.6,0.6,0.6))
  mpl.legend(loc=4)
  mpl.title(title)
  
  return figure


def _plot_scores_hist(figsize, scoresTarget, scoresNonTarget, title):
  figure = mpl.figure(figsize=figsize)
  
  # plot scoresTarget
  n, bins, patches = mpl.hist(scoresTarget, 50, normed=1, histtype='stepfilled', facecolor='b', alpha=0.75)

  # plot scoresNonTarget
  n, bins, patches = mpl.hist(scoresNonTarget, 50, normed=1, histtype='stepfilled', facecolor='r', alpha=0.75)
  
  mpl.legend(["Target scores", "NonTarget scores"])

  # finalize plot
  mpl.xlabel('Scores norm')
  mpl.ylabel('Hist')
  mpl.grid(True, color=(0.6,0.6,0.6))
  mpl.legend(loc=4)

  mpl.title(title)

  return figure



def main(command_line_parameters=None):
  """Reads score files, computes error measures and plots curves."""

  args = command_line_arguments(command_line_parameters)
  #print args
  # get some colors for plotting
  cmap = mpl.cm.get_cmap(name='hsv')
  colors = [cmap(i) for i in numpy.linspace(0, 1.0, len(args.dev_files)+1)]

  score_parser = {'4column' : bob.measure.load.split_four_column, '5column' : bob.measure.load.split_five_column}[args.parser]
  ids_parser = {'4column' : bob.measure.load.four_column, '5column' : bob.measure.load.five_column}[args.parser]

  # First, read the score files
  utils.info("Loading %d score files of the development set" % len(args.dev_files))
  scores_dev = [score_parser(os.path.join(args.directory, f)) for f in args.dev_files]
  ids_dev = [ids_parser(os.path.join(args.directory, f)) for f in args.dev_files]
  id_dev = []
  for i in ids_dev[0]:
  	if i[0] == i[1]: id_dev.append(i + (1,)) 
  	else: id_dev.append(i + (0,)) 

  ids_dev = numpy.array(id_dev)
  if (args.norm == 'norm'):
    ids_dev[:,3]=ids_dev[:,3].astype(numpy.float64)/max(ids_dev[:,3].astype(numpy.float64))

  if args.eval_files:
    utils.info("Loading %d score files of the evaluation set" % len(args.eval_files))
    scores_eval = [score_parser(os.path.join(args.directory, f)) for f in args.eval_files]
    ids_eval = [ids_parser(os.path.join(args.directory, f)) for f in args.eval_files]
    id_eval = []
    for i in ids_eval[0]: 
      if i[0] == i[1]: id_eval.append(i + (1,)) 
      else: id_eval.append(i + (0,)) 

    ids_eval = numpy.array(id_eval)
    if (args.norm == 'norm'):
      ids_eval[:,3]=ids_eval[:,3].astype(numpy.float64)/max(ids_eval[:,3].astype(numpy.float64))

  if args.criterion:
    utils.info("Computing %s on the development " % args.criterion + ("and HTER on the evaluation set" if args.eval_files else "set"))
   	
    pdf = PdfPages(args.pdf)
    for i in range(len(scores_dev)):
      totalModels = numpy.unique(ids_dev[:,1])

      eer_mean, figure = _plot_scores((25,10), args, totalModels, ids_dev, 'development', "Fauna graph for development set")
      pdf.savefig(figure)
    
      # Plot the EER per model
      bob.io.base.save(eer_mean,'eer_per_model.mat')
      
      pdf.savefig(_plot_eer((25,10), eer_mean, "EER per model curve for development set"))

      # Plot the scores histogram
      scoresTarget = ids_dev[ids_dev[:,4]=='1',3].astype(numpy.float64)
      scoresNonTarget = ids_dev[ids_dev[:,4]=='0',3].astype(numpy.float64)    
      pdf.savefig(_plot_scores_hist((25,10), scoresTarget, scoresNonTarget, "Scores histogram for development set"))

    if args.eval_files:
      for i in range(len(scores_eval)):
        totalModels = numpy.unique(ids_eval[:,1])

        eer_mean, figure = _plot_scores((25,10), args, totalModels, ids_eval, 'evaluation', "Fauna graph for evaluation set")
        pdf.savefig(figure)
      
        # Plot the EER per model
        pdf.savefig(_plot_eer((25,10), eer_mean, "EER per model curve for evaluation set"))

        # Plot the scores histogram
        scoresTarget = ids_eval[ids_eval[:,4]=='1',3].astype(numpy.float64)
        scoresNonTarget = ids_eval[ids_eval[:,4]=='0',3].astype(numpy.float64)    
        pdf.savefig(_plot_scores_hist((25,10), scoresTarget, scoresNonTarget, "Scores histogram for evaluation set"))

    pdf.close()


