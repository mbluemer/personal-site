---
title: "Moving My Blog to AWS"
date: 2020-11-12T20:18:12-05:00
slug: publishing-blog-on-aws
---

Every month, like clockwork, I'd get a charge to my credit card for $10, a torturous drop to remind me of this, this website, the personal blog that I perennially re-design and post my commitment to filling it with words, but ultimately abandon, like the tulip that didn't make it through the spring frost. Or maybe more like an ugly weed. we'll never quite know until it peaks its head through.

This past month I saw that $10 charge and decided to do something about it. My site was being hosted on a [Linode](https://www.linode.com) server using self-hosted [Ghost](https://ghost.org), a much overpowered solution for a blog seeing no traffic. My idea of using that server to self host other personal software, like a wiki, was equally short lived. So instead of using wasted compute I thought, why not use the same tools that I use every day at work? I decided it was time to move to AWS. Specifically moving to host this site in S3 with CloudFront in front of it.

Other than a familiarity there were a couple of reasons I considered AWS attractive. First and foremost was the idea of cost savings. I say the "idea" because I wasn't, and still am not, entirely sure what it will cost to host this website on AWS. I've found the calculators hard to deal with, especially at such low numbers, but with traffic to the site almost non-existent the costs seemed like they'd be... well, non-existent! Okay not quite, so far I've paid $1 for the hosted zone in Route53 but that's it. Maybe I'll do an update down the line. Something key though is I have an alert to warn me if the cost goes above $10 in a month period. Assuming that alarm works, I'll immediately know when things become more expensive than my previous hosting.

Another personal plus was a learning opportunity in both AWS in general and, because everyone is talking about it, the [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/home.html). At work I've been thrust into CloudFormation and the experience so far has been sub-par so I wanted to try out CDK. Definitely too early to tell how I feel about it but good experience nonetheless.

## What Can Go Wrong Will Go Wrong

I went into this thinking things would be easy. CDK is supposed to simplify the creation of infrastructure by doing a bunch of behind the scenes work and I've set up at least one S3 website fronted by CloudFront before. But of course nothing is ever that easy and the mistakes along the way are alays obvious in hindsight. The following are some of my mistakes and lessons.

### CDK Shared Libraries

They aren't quite there yet. The AWS CDK constructs library comes with three construct levels: constructs that directly correspond to CloudFormation resources, constructs that correspond to an AWS concept and do a bit of hand holding with best practices, and constructs that are considered solutions, sometimes utilizing multiple AWS services. I was sort of hoping to hit that third level construct to build this site but AWS doesn't have many so I turned to third parties.

I found a [cloudcomponents library](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-static-website) for hosting static websites. This required some experimentation before I decided to actually read into what the library was doing and realizing I needed a hosted zone already set up with my domain. With the dependencies for these constructs hidden away and the lack of control I had I decided at this point to just create everything I needed with the AWS constructs.

### Just Use Route53

The domain name for this blog was purchased from Google Domains so it, and now the rest of my domains, lives there. Most of the blog posts or tutorials I read on setting up a website in AWS reference using Route53 to set up your domain causing some knee jerk frustration. I went through the process of moving a domain name from one provider to another when I moved to Google Domains and I didn't want to do that again. I also didn't want to lock myself completely into AWS's ecosystem. So I tried going without it, creating a DNS validated certificate and manually creating the proper DNS entries in Google Domains. But wait, then I needed to manually create an A record too?

It turns out I just didn't fully understand DNS and who did what job. I could keep my Domain Name registered with Google Domains, set up a hosted zone in Route53, and just point Google Domains to the hosted zone's NS records. Now pretty much everything was managed by CDK and all I had to do manually was copy the NS records. The lesson here being understand your technology before cursing it and just use Route53.

### CloudFront and S3 Aren't Made for Websites

Or at the least that's not their sole intent. S3 itself is pretty decent at hosting a static website but it doesn't support SSL. CloudFront supports SSL but it doesn't come with the niceties that S3 does and so I spent quite a bit of time chasing the perfect solution when it didn't exist. Let me elaborate.

A super basic solution for an S3 website is to throw your static content into a bucket and [enable website hosting](https://docs.aws.amazon.com/AmazonS3/latest/dev/EnableWebsiteHosting.html). You're then able to [configure an index document](https://docs.aws.amazon.com/AmazonS3/latest/dev/IndexDocumentSupport.html) and [configure an error document](https://docs.aws.amazon.com/AmazonS3/latest/dev/CustomErrorDocSupport.html) for some easy customization, some great out of the box features. You don't get SSL though. It's not supported... like at all.

So in comes CloudFront, which does support SSL. And what do you know, in CloudFront there's a concept of an "S3 Origin", perfect! This even allows you to keep your bucket completely private, ensuring encrypted communication all the way through. So I set that up in CDK, making sure to set the `defaultRootObject` to `index.html` and it seemed like it was working, at the https://theblue.dev was serving the right thing. But as soon as I clicked I link I was served with a 403, access denied. Turns out subdomains weren't respecting the default object of `index.html`, CloudFront only served it properly at the root.

Thanks to StackExchange I found [an answer](https://serverfault.com/a/776143). I'd need to make my S3 bucket public again and reference it in CloudFront as a Custom Origin, rather than an S3 Origin, using the website URL. Now nothing worked, I was just getting timeouts! This is when I lost hope and walked away from the problem for a couple of days.

In a flash of inspiration I decided to resort to a sadistic method of figuring out the problem. I followed a tutorial to set everything up by hand, parallel to my CDK configuration, and then took screenshots of every configuration screen to compare all of the settings. One advantage of CDK is that it uses better defaults than using the AWS Console, in this case setting my Origin Protocol Policy to `HTTPS_ONLY`. Well this meant it was calling out to the s3 website, which doesn't support SSL, asking for an SSL connection and S3's response was to fail in the most uninformative manner, to timeout. I flipped the Origin Protocol Policy to `HTTP_ONLY` and everything worked! Subdomains were now properly returning `index.html`.

Okay okay, that was a lot and that should have been it but I couldn't let myself stop there. This configuration means that there's unencrypted traffic in the chain and my buckets are still public; there had to be a better way. After some digging the closest thing I could find was using a [Lambda@Edge](https://docs.aws.amazon.com/lambda/latest/dg/lambda-edge.html) function to manipulate any requests to a bare subdomain to point at `index.html` for that subdomain. A Lambda call for every request though? Ick! Given this is just a blog with some plain text I decided this wasn't worth pursuing and so stuck with my existing setup.

## Well It's Up and Running

Tada! Something like 5 frustrating hours later and I have... the exact same site, just running somewhere else. It was all very anti-climactic and yet it still felt pretty good to finally get everything working. If you want to check out the CDK I ended up with the GitLab repo is public [here](https://gitlab.com/mbluemer/personal-site). I make no promises that this code is ideal as this is my first real foray into CDK but maybe it'll get refactored over time.

Cheers! 🍻