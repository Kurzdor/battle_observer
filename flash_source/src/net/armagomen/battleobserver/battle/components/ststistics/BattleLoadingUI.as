package net.armagomen.battleobserver.battle.components.ststistics
{
	import flash.events.Event;
	import flash.geom.ColorTransform;
	import flash.text.TextFieldAutoSize;
	import flash.utils.setTimeout;
	import net.armagomen.battleobserver.battle.base.ObserverBattleDisplayable;
	import net.armagomen.battleobserver.utils.Utils;
	
	public class BattleLoadingUI extends ObserverBattleDisplayable
	{
		private var loading:*;
		public var py_getStatisticString:Function;
		public var py_getIconColor:Function;
		public var py_getIconMultiplier:Function;
		public var py_statisticEnabled:Function;
		public var py_iconEnabled:Function;
		private var namesCache:Object         = new Object();
		private var statisticsEnabled:Boolean = false;
		private var iconEnabled:Boolean       = false;
		private var count:Number              = 0;
		
		public function BattleLoadingUI(loading:*)
		{
			this.loading = loading;
			super();
		}
		
		override public function as_onAfterPopulate():void
		{
			super.as_onAfterPopulate();
			this.statisticsEnabled = py_statisticEnabled();
			this.iconEnabled = py_iconEnabled();
			this.loading.addEventListener(Event.CHANGE, this.onChange);
			this.addListeners();
		}
		
		override protected function onBeforeDispose():void
		{
			this.as_clear();
			this.loading.removeEventListener(Event.CHANGE, this.onChange);
			super.onBeforeDispose();
		}
		
		public function as_clear():void
		{
			this.removeListeners();
			App.utils.data.cleanupDynamicObject(this.namesCache);
		}
		
		private function onChange(eve:Event):void
		{
			this.as_clear();
			this.addListeners();
		}
		
		private function timeout():void
		{
			this.count++;
			if (count < 100)
			{
				setTimeout(this.addListeners, 100);
			}
		}
		
		private function addListeners():void
		{
			if (!this.loading.form || !this.loading.form._allyRenderers || !this.loading.form._allyRenderers[0].model)
			{
				this.timeout();
				return;
			}
			for each (var ally:* in this.loading.form._allyRenderers)
			{
				this.addListener(ally)
			}
			for each (var enemy:* in this.loading.form._enemyRenderers)
			{
				this.addListener(enemy)
			}
		}
		
		private function addListener(item:*):void
		{
			var icon:*                = item._vehicleIcon;
			var tColor:ColorTransform = new ColorTransform();
			tColor.color = Utils.colorConvert(py_getIconColor(item.model.vehicleType));
			tColor.redMultiplier = tColor.greenMultiplier = tColor.blueMultiplier = py_getIconMultiplier();
			icon.cTansform = tColor;
			icon.item = item;
			if (!icon.hasEventListener(Event.RENDER))
			{
				icon.addEventListener(Event.RENDER, this.onRenderHendle);
			}
			if (this.statisticsEnabled)
			{
				this.namesCache[item.model.accountDBID] = py_getStatisticString(item.model.accountDBID, item._isEnemy, item.model.clanAbbrev);
				item._textField.autoSize = item._isEnemy ? TextFieldAutoSize.RIGHT : TextFieldAutoSize.LEFT;
			}
		}
		
		private function removeListeners():void
		{
			if (!this.loading.form)
			{
				this.timeout();
				return;
			}
			for each (var ally:* in this.loading.form._allyRenderers)
			{
				this.removeListener(ally)
			}
			for each (var enemy:* in this.loading.form._enemyRenderers)
			{
				this.removeListener(enemy)
			}
		}
		
		private function removeListener(item:*):void
		{
			if (!item || !item._vehicleIcon)
			{
				return;
			}
			if (item._vehicleIcon.hasEventListener(Event.RENDER))
			{
				item._vehicleIcon.removeEventListener(Event.RENDER, this.onRenderHendle);
			}
		}
		
		private function onRenderHendle(eve:Event):void
		{
			var icon:* = eve.target;
			if (this.iconEnabled)
			{
				icon.transform.colorTransform = icon.cTansform;
			}
			if (this.statisticsEnabled)
			{
				this.setPlayerText(icon.item);
			}
		}
		
		private function setPlayerText(item:*):void
		{
			if (item.model.accountDBID != 0 && this.namesCache[item.model.accountDBID])
			{
				item._textField.htmlText = this.namesCache[item.model.accountDBID];
			}
		}
	}
}